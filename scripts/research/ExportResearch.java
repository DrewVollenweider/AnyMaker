// Export selected, hash-validated GCL records; no automatic whole-file analysis.
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

public class ExportResearch extends GhidraScript {
  public void run() throws Exception {
    String[] args = getScriptArgs();
    if (args.length != 2) throw new IllegalArgumentException("plan.tsv output-directory");
    Path out = Paths.get(args[1]);
    Files.createDirectories(out);
    List<String[]> funcs = new ArrayList<>();
    for (String line : Files.readAllLines(Paths.get(args[0]), StandardCharsets.UTF_8)) {
      String[] p = line.split("\t", 5);
      if (p[0].equals("R")) {
        Address a = toAddr(Long.parseLong(p[1]));
        createLabel(a, p[3], true);
        setEOLComment(a, "Unresolved GCL relocation kind=" + p[2] + " symbol=" + p[4]);
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
        Function f = currentProgram.getFunctionManager().createFunction(p[3], start, body, SourceType.USER_DEFINED);
        if (f == null) throw new IllegalStateException("Cannot create " + p[3]);
        setPlateComment(start, "GCL signature: " + p[4] + "\nTypes/relocations unresolved. Pseudocode is approximate.");
        StringBuilder listing = new StringBuilder("# " + p[4] + "\n");
        InstructionIterator it = currentProgram.getListing().getInstructions(body, true);
        while (it.hasNext()) {
          Instruction ins = it.next();
          StringBuilder hex = new StringBuilder();
          for (byte b : ins.getBytes()) hex.append(String.format("%02x", b & 255));
          listing.append(ins.getAddress()).append("\t").append(hex).append("\t").append(ins).append("\n");
        }
        Files.writeString(out.resolve(p[3] + ".asm.tsv"), listing.toString(), StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
        DecompileResults result = decompiler.decompileFunction(f, 60, monitor);
        String text = result.decompileCompleted() ? result.getDecompiledFunction().getC() : "ERROR: " + result.getErrorMessage();
        Files.writeString(out.resolve(p[3] + ".c"), text, StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
        println("RESEARCH_EXPORT " + p[3] + " decompiled=" + result.decompileCompleted());
      }
    } finally { decompiler.dispose(); }
  }
}
