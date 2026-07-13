// Print instructions whose explicit scalar operands match one of the supplied
// integer values.  Arguments accept decimal or Java-style hex (0x...).
// @category NOBU16

import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.scalar.Scalar;

import java.util.HashSet;
import java.util.Set;

public class FindScalarImmediate extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length == 0) {
            throw new IllegalArgumentException("pass one or more integer values");
        }

        Set<Long> wanted = new HashSet<>();
        for (String argument : arguments) {
            wanted.add(Long.decode(argument));
        }

        for (Instruction instruction : currentProgram.getListing().getInstructions(true)) {
            for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
                for (Object object : instruction.getOpObjects(operand)) {
                    if (!(object instanceof Scalar)) {
                        continue;
                    }
                    Scalar scalar = (Scalar) object;
                    long unsignedValue = scalar.getUnsignedValue();
                    long signedValue = scalar.getSignedValue();
                    if (!wanted.contains(unsignedValue) && !wanted.contains(signedValue)) {
                        continue;
                    }
                    Function function = getFunctionContaining(instruction.getAddress());
                    println(instruction.getAddress() + " " +
                        (function == null ? "<no-function>" :
                            function.getName() + "@" + function.getEntryPoint()) +
                        " operand=" + operand + " value=" + unsignedValue +
                        " :: " + instruction);
                }
            }
        }
    }
}
