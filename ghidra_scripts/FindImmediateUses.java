// Find true scalar/immediate operands, excluding memory displacements.
// First argument is output path; remaining arguments are hexadecimal values.
// @category NOBU16

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.lang.OperandType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.scalar.Scalar;

import java.io.File;
import java.io.PrintWriter;
import java.util.HashSet;
import java.util.Set;

public class FindImmediateUses extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) throw new IllegalArgumentException("output path and hex values required");
        File output = new File(args[0]);
        output.getParentFile().mkdirs();
        Set<Long> wanted = new HashSet<>();
        for (int i = 1; i < args.length; i++) {
            String s = args[i].toLowerCase().replace("0x", "");
            wanted.add(Long.parseUnsignedLong(s, 16));
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
                        if ((ins.getOperandType(op) & OperandType.SCALAR) == 0) continue;
                        for (Object obj : ins.getOpObjects(op)) {
                            if (!(obj instanceof Scalar)) continue;
                            long value = ((Scalar)obj).getUnsignedValue();
                            if (!wanted.contains(value)) continue;
                            Function f = currentProgram.getFunctionManager().getFunctionContaining(ins.getAddress());
                            String fn = f == null ? "<no-function>" : f.getName() + "@" + f.getEntryPoint();
                            out.println(ins.getAddress() + " " + fn + " operand=" + op +
                                " value=0x" + Long.toHexString(value) + " :: " + ins);
                        }
                    }
                }
            }
        }
        println("output=" + output.getAbsolutePath());
    }
}
