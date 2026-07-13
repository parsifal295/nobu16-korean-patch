// Disassemble, create, and decompile selected function entry points in a
// minimally imported program.  This avoids running whole-program analysis on
// the very large NOBU16 executable when only a few configuration functions are
// needed.
// @category NOBU16

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.Reference;

public class CreateDecompileTargets extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length == 0) {
            throw new IllegalArgumentException("pass one or more function entry addresses");
        }

        for (String argument : arguments) {
            Address entry = currentProgram.getAddressFactory().getAddress(argument);
            if (getInstructionAt(entry) == null) {
                disassemble(entry);
            }
            Function function = getFunctionAt(entry);
            if (function == null) {
                function = createFunction(entry, null);
            }
            println("PREPARED " + argument + " " +
                (function == null ? "<no-function>" : function.getName()));
        }

        analyzeChanges(currentProgram);

        DecompInterface decompiler = new DecompInterface();
        decompiler.openProgram(currentProgram);
        try {
            for (String argument : arguments) {
                Address entry = currentProgram.getAddressFactory().getAddress(argument);
                Function function = getFunctionAt(entry);
                if (function == null) {
                    println("NO_FUNCTION " + argument);
                    continue;
                }

                println("===== " + function.getName() + " @ " +
                    function.getEntryPoint() + " =====");
                DecompileResults results = decompiler.decompileFunction(function, 120, monitor);
                if (!results.decompileCompleted()) {
                    println("DECOMPILE_FAILED " + results.getErrorMessage());
                }
                else {
                    println(results.getDecompiledFunction().getC());
                }

                println("----- CALL/REFERENCE OPERANDS -----");
                Instruction instruction = getInstructionAt(function.getBody().getMinAddress());
                while (instruction != null && function.getBody().contains(instruction.getAddress())) {
                    Reference[] references = instruction.getReferencesFrom();
                    for (Reference reference : references) {
                        println(instruction.getAddress() + " " + instruction + " -> " +
                            reference.getToAddress() + " " + reference.getReferenceType());
                    }
                    instruction = instruction.getNext();
                }
            }
        }
        finally {
            decompiler.dispose();
        }
    }
}
