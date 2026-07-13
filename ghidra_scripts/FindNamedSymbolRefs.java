// @category NOBU16
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;

public class FindNamedSymbolRefs extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length == 0) {
            throw new IllegalArgumentException("case-insensitive symbol-name fragments required");
        }
        SymbolIterator symbols = currentProgram.getSymbolTable().getAllSymbols(true);
        while (symbols.hasNext()) {
            Symbol symbol = symbols.next();
            String lower = symbol.getName().toLowerCase();
            boolean match = false;
            for (String arg : args) {
                if (lower.contains(arg.toLowerCase())) {
                    match = true;
                    break;
                }
            }
            if (!match) {
                continue;
            }
            println("SYMBOL " + symbol.getName() + " @ " + symbol.getAddress() + " " + symbol.getSymbolType());
            ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(symbol.getAddress());
            while (refs.hasNext()) {
                Reference ref = refs.next();
                Function caller = getFunctionContaining(ref.getFromAddress());
                println(" REF " + ref.getFromAddress() + " " + ref.getReferenceType() + " " +
                    (caller == null ? "<no-function>" : caller.getName() + "@" + caller.getEntryPoint()));
            }
        }
    }
}
