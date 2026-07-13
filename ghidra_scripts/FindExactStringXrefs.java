// Find references to defined strings whose value exactly matches an argument.
// @category NOBU16

import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

import java.util.HashSet;
import java.util.Set;

public class FindExactStringXrefs extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length == 0) {
            throw new IllegalArgumentException("one or more exact string values required");
        }
        Set<String> wanted = new HashSet<>();
        for (String arg : args) wanted.add(arg);

        for (Data data : currentProgram.getListing().getDefinedData(true)) {
            if (!data.hasStringValue() || data.getValue() == null) continue;
            String value = data.getValue().toString();
            if (!wanted.contains(value)) continue;
            println("STRING " + data.getAddress() + " " + value);
            ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(data.getAddress());
            while (refs.hasNext()) {
                Reference ref = refs.next();
                Function function = getFunctionContaining(ref.getFromAddress());
                println("  REF " + ref.getFromAddress() + " " +
                    (function == null ? "<no-function>" :
                        function.getName() + "@" + function.getEntryPoint()));
            }
        }
    }
}
