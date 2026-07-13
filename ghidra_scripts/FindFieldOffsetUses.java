// Find every instruction operand containing one of the requested scalar values,
// including memory displacements. First argument is output path; remaining
// arguments are hexadecimal scalar values.
// @category NOBU16

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.scalar.Scalar;

import java.io.File;
import java.io.PrintWriter;
import java.util.HashSet;
import java.util.Set;

public class FindFieldOffsetUses extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) {
            throw new IllegalArgumentException("output path and hex values required");
        }
        File output = new File(args[0]);
        output.getParentFile().mkdirs();
        Set<Long> wanted = new HashSet<>();
        for (int i = 1; i < args.length; i++) {
            wanted.add(Long.parseUnsignedLong(args[i].toLowerCase().replace("0x", ""), 16));
        }

        Listing listing = currentProgram.getListing();
        try (PrintWriter out = new PrintWriter(output, "UTF-8")) {
            out.println("program=" + currentProgram.getName());
            out.println("wanted=" + wanted);
            for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
                if (!block.isExecute()) continue;
                AddressSet set = new AddressSet(block.getStart(), block.getEnd());
                for (Instruction ins : listing.getInstructions(set, true)) {
                    for (int op = 0; op < ins.getNumOperands(); op++) {
                        boolean hit = false;
                        for (Object obj : ins.getOpObjects(op)) {
                            if (obj instanceof Scalar &&
                                wanted.contains(((Scalar)obj).getUnsignedValue())) {
                                hit = true;
                                break;
                            }
                        }
                        if (!hit) continue;
                        Function f = currentProgram.getFunctionManager()
                            .getFunctionContaining(ins.getAddress());
                        String fn = f == null ? "<no-function>" :
                            f.getName() + "@" + f.getEntryPoint();
                        out.println(ins.getAddress() + " " + fn + " operand=" + op +
                            " :: " + ins);
                    }
                }
            }
        }
        println("output=" + output.getAbsolutePath());
    }
}
