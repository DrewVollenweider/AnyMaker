// Mark the entry point of an extracted native GCL constructor.
// @category Anymaker
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;

public class SetupSample extends GhidraScript {
    public void run() throws Exception {
        Address base = currentProgram.getMinAddress();
        disassemble(base);
        createFunction(base, currentProgram.getName().replace('.', '_'));
    }
}
