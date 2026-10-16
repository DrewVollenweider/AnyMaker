// Export static, approximate C code from the imported COPY of game.exe.
// @category Anymaker
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import java.io.*;
import java.nio.charset.StandardCharsets;

public class ExportAnymaker extends GhidraScript {
    public void run() throws Exception {
        File out = new File(getScriptArgs()[0]);
        if (out.exists()) throw new IOException("Refusing to overwrite output");
        DecompInterface d = new DecompInterface();
        d.openProgram(currentProgram);
        int total=0, success=0;
        try (PrintWriter w = new PrintWriter(new OutputStreamWriter(new FileOutputStream(out), StandardCharsets.UTF_8))) {
            w.println("/* APPROXIMATE GHIDRA OUTPUT. Not original source. Imported file: " + currentProgram.getName() + ". */");
            FunctionIterator fs = currentProgram.getFunctionManager().getFunctions(true);
            while (fs.hasNext() && !monitor.isCancelled()) {
                Function f = fs.next(); total++;
                if (f.isExternal() || f.isThunk()) continue;
                DecompileResults r = d.decompileFunction(f, 20, monitor);
                w.println("\n/* " + f.getEntryPoint() + " " + f.getName() + " */");
                if (r.decompileCompleted() && r.getDecompiledFunction()!=null) {
                    w.println(r.getDecompiledFunction().getC()); success++;
                } else w.println("/* Decompilation unavailable for this function. */");
                if (total % 500 == 0) println("Exported " + success + " functions; visited " + total);
            }
        } finally { d.dispose(); }
        println("EXPORT COMPLETE: " + success + " decompiled; " + total + " functions visited.");
    }
}
