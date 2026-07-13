// Decompile functions and write the C output to a UTF-8 report.
// Args: output function-address...
// @category NOBU16

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import java.io.File;
import java.io.PrintWriter;

public class DecompileToFile extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) throw new IllegalArgumentException("output function-address...");
        File output = new File(args[0]);
        output.getParentFile().mkdirs();
        DecompInterface decompiler = new DecompInterface();
        decompiler.openProgram(currentProgram);
        try (PrintWriter out = new PrintWriter(output, "UTF-8")) {
            for (int i = 1; i < args.length; i++) {
                Address address = currentProgram.getAddressFactory().getAddress(args[i]);
                Function function = currentProgram.getFunctionManager().getFunctionContaining(address);
                if (function == null) { out.println("NO_FUNCTION " + args[i]); continue; }
                out.println("===== " + function.getName() + " @ " + function.getEntryPoint() + " =====");
                DecompileResults results = decompiler.decompileFunction(function, 120, monitor);
                if (!results.decompileCompleted()) {
                    out.println("DECOMPILE_FAILED " + results.getErrorMessage());
                    continue;
                }
                out.println(results.getDecompiledFunction().getC());
            }
        } finally {
            decompiler.dispose();
        }
        println("output=" + output.getAbsolutePath());
    }
}
