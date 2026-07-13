import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

public class DecompileAt extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length == 0) {
            throw new IllegalArgumentException("pass one or more function addresses");
        }
        DecompInterface decompiler = new DecompInterface();
        decompiler.openProgram(currentProgram);
        try {
            for (String argument : arguments) {
                Address address = currentProgram.getAddressFactory().getAddress(argument);
                Function function = currentProgram.getFunctionManager()
                    .getFunctionContaining(address);
                if (function == null) {
                    println("NO_FUNCTION " + argument);
                    continue;
                }
                println("===== " + function.getName() + " @ " + function.getEntryPoint() + " =====");
                DecompileResults results = decompiler.decompileFunction(function, 60, monitor);
                if (!results.decompileCompleted()) {
                    println("DECOMPILE_FAILED " + results.getErrorMessage());
                    continue;
                }
                println(results.getDecompiledFunction().getC());
            }
        } finally {
            decompiler.dispose();
        }
    }
}
