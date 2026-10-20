// Export selected native PE spans; no automatic whole-file analysis.
//@category Anymaker
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.decompiler.*;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.pcode.*;

public class ExportNative extends GhidraScript {
  private static String json(String value) {
    if (value == null) return "null";
    StringBuilder s = new StringBuilder("\"");
    for (char c : value.toCharArray()) {
      switch (c) {
        case '"': s.append("\\\""); break;
        case '\\': s.append("\\\\"); break;
        case '\n': s.append("\\n"); break;
        case '\r': s.append("\\r"); break;
        case '\t': s.append("\\t"); break;
        default:
          if (c < 32) s.append(String.format("\\u%04x", (int)c));
          else s.append(c);
      }
    }
    return s.append('"').toString();
  }

  private static String varnode(Varnode v) {
    if (v == null) return "null";
    return "{\"space\":" + json(v.getAddress().getAddressSpace().getName()) +
      ",\"offset\":" + json(Long.toUnsignedString(v.getOffset())) +
      ",\"size\":" + v.getSize() + ",\"constant\":" + v.isConstant() +
      ",\"register\":" + v.isRegister() + ",\"unique\":" + v.isUnique() + "}";
  }

  private void exportFacts(Path path, String[] plan, AddressSet body, boolean completed) throws Exception {
    StringBuilder s = new StringBuilder("{\"schema\":1,\"signature\":").append(json(plan[4]))
      .append(",\"code_offset\":").append(plan[1]).append(",\"code_size\":").append(plan[2])
      .append(",\"export_name\":").append(json(plan[3])).append(",\"decompile_completed\":")
      .append(completed).append(",\"instructions\":[");
    boolean first = true;
    InstructionIterator it = currentProgram.getListing().getInstructions(body, true);
    while (it.hasNext()) {
      monitor.checkCancelled();
      Instruction ins = it.next();
      if (!first) s.append(','); first = false;
      StringBuilder hex = new StringBuilder();
      for (byte b : ins.getBytes()) hex.append(String.format("%02x", b & 255));
      s.append("{\"address\":").append(json(Long.toUnsignedString(ins.getAddress().getOffset())))
        .append(",\"bytes\":").append(json(hex.toString())).append(",\"mnemonic\":")
        .append(json(ins.getMnemonicString())).append(",\"text\":").append(json(ins.toString()))
        .append(",\"flow_type\":").append(json(ins.getFlowType().toString()))
        .append(",\"fallthrough\":").append(ins.getFallThrough() == null ? "null" :
          json(Long.toUnsignedString(ins.getFallThrough().getOffset()))).append(",\"references\":[");
      boolean firstRef = true;
      for (Reference ref : currentProgram.getReferenceManager().getReferencesFrom(ins.getAddress())) {
        if (!firstRef) s.append(','); firstRef = false;
        s.append("{\"space\":").append(json(ref.getToAddress().getAddressSpace().getName()))
          .append(",\"target\":").append(json(Long.toUnsignedString(ref.getToAddress().getOffset())))
          .append(",\"type\":").append(json(ref.getReferenceType().toString()))
          .append(",\"operand\":").append(ref.getOperandIndex()).append('}');
      }
      s.append("],\"pcode\":[");
      boolean firstOp = true;
      for (PcodeOp op : ins.getPcode()) {
        if (!firstOp) s.append(','); firstOp = false;
        s.append("{\"opcode\":").append(json(op.getMnemonic())).append(",\"output\":")
          .append(varnode(op.getOutput())).append(",\"inputs\":[");
        for (int i = 0; i < op.getNumInputs(); i++) {
          if (i > 0) s.append(','); s.append(varnode(op.getInput(i)));
        }
        s.append("]}");
      }
      s.append("]}");
    }
    s.append("]}\n");
    Files.writeString(path, s.toString(), StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
  }

  public void run() throws Exception {
    String[] args = getScriptArgs();
    if (args.length != 2 && args.length != 3) throw new IllegalArgumentException("plan.tsv output-directory [assembly-only]");
    boolean assemblyOnly = args.length == 3 && args[2].equals("assembly-only");
    if (args.length == 3 && !assemblyOnly) throw new IllegalArgumentException("Unknown export mode");
    Path out = Paths.get(args[1]);
    Files.createDirectories(out);
    List<String[]> funcs = new ArrayList<>();
    for (String line : Files.readAllLines(Paths.get(args[0]), StandardCharsets.UTF_8)) {
      String[] p = line.split("\t", 5);
      if (p[0].equals("R")) {
        Address a = toAddr(Long.parseLong(p[1]));
        createLabel(a, p[3], true);
        setEOLComment(a, "Unresolved operand kind=" + p[2] + " symbol=" + p[4]);
      } else if (p[0].equals("F")) funcs.add(p);
    }
    DecompInterface decompiler = new DecompInterface();
    decompiler.openProgram(currentProgram);
    try {
      for (String[] p : funcs) {
        monitor.checkCancelled();
        Address start = toAddr(Long.parseLong(p[1]));
        long size = Long.parseLong(p[2]);
        AddressSet body = new AddressSet(start, start.add(size - 1));
        new DisassembleCommand(start, body, true).applyTo(currentProgram, monitor);
        Function f = currentProgram.getFunctionManager().getFunctionAt(start);
        if (f == null) f = currentProgram.getFunctionManager().createFunction(p[3], start, body, SourceType.USER_DEFINED);
        else { f.setBody(body); f.setName(p[3], SourceType.USER_DEFINED); }
        if (f == null) throw new IllegalStateException("Cannot create " + p[3]);
        setPlateComment(start, "Native PE selection: " + p[4] + "\nFunction identity/ABI unresolved. Pseudocode is approximate.");
        StringBuilder listing = new StringBuilder("# " + p[4] + "\n");
        InstructionIterator it = currentProgram.getListing().getInstructions(body, true);
        while (it.hasNext()) {
          Instruction ins = it.next();
          StringBuilder hex = new StringBuilder();
          for (byte b : ins.getBytes()) hex.append(String.format("%02x", b & 255));
          listing.append(ins.getAddress()).append("\t").append(hex).append("\t").append(ins).append("\n");
        }
        Files.writeString(out.resolve(p[3] + ".asm.tsv"), listing.toString(), StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
        DecompileResults result = assemblyOnly ? null : decompiler.decompileFunction(f, 60, monitor);
        boolean completed = result != null && result.decompileCompleted();
        String text = assemblyOnly ? "/* Static disassembly only; no pseudocode requested. */\n" :
          completed ? result.getDecompiledFunction().getC() : "ERROR: " + result.getErrorMessage();
        Files.writeString(out.resolve(p[3] + ".c"), text, StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
        exportFacts(out.resolve(p[3] + ".facts.json"), p, body, completed);
        println("RESEARCH_EXPORT " + p[3] + " decompiled=" + completed + " assembly_only=" + assemblyOnly);
      }
    } finally { decompiler.dispose(); }
  }
}



