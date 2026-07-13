// @category NOBU16
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import java.io.File;
import java.io.PrintWriter;

public class DecompileFunctionsToFile extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) throw new IllegalArgumentException("output path then addresses required");
        File output = new File(args[0]);
        output.getParentFile().mkdirs();
        PrintWriter writer = new PrintWriter(output, "UTF-8");
        DecompInterface decompiler = new DecompInterface();
        decompiler.openProgram(currentProgram);
        try {
            for (int i = 1; i < args.length; i++) {
                Address address = currentProgram.getAddressFactory().getAddress(args[i]);
                Function function = currentProgram.getFunctionManager().getFunctionContaining(address);
                if (function == null) {
                    writer.println("NO_FUNCTION " + args[i]);
                    continue;
                }
                writer.println("===== " + function.getName() + " @ " + function.getEntryPoint() + " =====");
                DecompileResults results = decompiler.decompileFunction(function, 120, monitor);
                if (!results.decompileCompleted()) {
                    writer.println("DECOMPILE_FAILED " + results.getErrorMessage());
                    continue;
                }
                writer.println(results.getDecompiledFunction().getC());
            }
        } finally {
            decompiler.dispose();
            writer.close();
        }
        println("WROTE " + output.getAbsolutePath());
    }
}
