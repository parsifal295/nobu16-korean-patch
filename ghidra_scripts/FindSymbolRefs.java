// Locate named symbols/imports and print every direct reference to them.
// @category NOBU16

import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;

public class FindSymbolRefs extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length == 0) {
            throw new IllegalArgumentException("pass one or more case-insensitive symbol substrings");
        }

        SymbolIterator symbols = currentProgram.getSymbolTable().getAllSymbols(true);
        while (symbols.hasNext()) {
            Symbol symbol = symbols.next();
            String lowerName = symbol.getName().toLowerCase();
            boolean matched = false;
            for (String argument : arguments) {
                if (lowerName.contains(argument.toLowerCase())) {
                    matched = true;
                    break;
                }
            }
            if (!matched) {
                continue;
            }

            println("SYMBOL " + symbol.getName(true) + " @ " + symbol.getAddress() +
                " type=" + symbol.getSymbolType());
            ReferenceIterator references = currentProgram.getReferenceManager()
                .getReferencesTo(symbol.getAddress());
            while (references.hasNext()) {
                Reference reference = references.next();
                Function function = getFunctionContaining(reference.getFromAddress());
                println("  REF " + reference.getFromAddress() + " " +
                    (function == null ? "<no-function>" :
                        function.getName() + "@" + function.getEntryPoint()) + " " +
                    reference.getReferenceType());
            }
        }
    }
}
