// Find scalar operands (including memory displacements) inside an address range.
// Args: output, start, end, hex values...
// @category NOBU16

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.scalar.Scalar;

import java.io.File;
import java.io.PrintWriter;
import java.util.HashSet;
import java.util.Set;

public class FindScalarUsesInRange extends GhidraScript {
    private long parseHex(String s) {
        return Long.parseUnsignedLong(s.toLowerCase().replace("0x", ""), 16);
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 4) throw new IllegalArgumentException("output start end values...");
        File output = new File(args[0]);
        output.getParentFile().mkdirs();
        Address start = currentProgram.getAddressFactory().getAddress(args[1]);
        Address end = currentProgram.getAddressFactory().getAddress(args[2]);
        Set<Long> wanted = new HashSet<>();
        for (int i = 3; i < args.length; i++) wanted.add(parseHex(args[i]));
        try (PrintWriter out = new PrintWriter(output, "UTF-8")) {
            AddressSet set = new AddressSet(start, end);
            for (Instruction ins : currentProgram.getListing().getInstructions(set, true)) {
                boolean hit = false;
                for (int op = 0; op < ins.getNumOperands(); op++) {
                    for (Object obj : ins.getOpObjects(op)) {
                        if (obj instanceof Scalar && wanted.contains(((Scalar)obj).getUnsignedValue())) {
                            hit = true;
                        }
                    }
                }
                if (!hit) continue;
                Function f = currentProgram.getFunctionManager().getFunctionContaining(ins.getAddress());
                String fn = f == null ? "<no-function>" : f.getName() + "@" + f.getEntryPoint();
                out.println(ins.getAddress() + " " + fn + " :: " + ins);
            }
        }
        println("output=" + output.getAbsolutePath());
    }
}
