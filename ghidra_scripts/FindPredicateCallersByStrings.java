// Find callers of a predicate that also reference interesting ASCII/Unicode strings.
// @category NOBU16

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

public class FindPredicateCallersByStrings extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) {
            println("usage: FindPredicateCallersByStrings.java <predicate-address> [keyword ...]");
            return;
        }

        Set<String> keywords = new HashSet<>();
        if (args.length == 1) {
            Collections.addAll(keywords,
                "castle", "map", "field", "kyoten", "base", "name", "shiro", "jou");
        }
        else {
            for (int i = 1; i < args.length; i++) {
                keywords.add(args[i].toLowerCase(Locale.ROOT));
            }
        }

        Address target = currentProgram.getAddressFactory().getAddress(args[0]);
        FunctionManager fm = currentProgram.getFunctionManager();
        Set<Address> callers = new HashSet<>();
        ReferenceIterator predicateRefs = currentProgram.getReferenceManager().getReferencesTo(target);
        while (predicateRefs.hasNext()) {
            Reference ref = predicateRefs.next();
            Function f = fm.getFunctionContaining(ref.getFromAddress());
            if (f != null) {
                callers.add(f.getEntryPoint());
            }
        }
        println("PREDICATE " + target + " UNIQUE_CALLERS " + callers.size());

        Map<Address, List<String>> matches = new HashMap<>();
        Listing listing = currentProgram.getListing();
        for (Data data : listing.getDefinedData(true)) {
            if (!data.hasStringValue()) {
                continue;
            }
            Object value = data.getValue();
            if (value == null) {
                continue;
            }
            String stringValue = value.toString();
            String lower = stringValue.toLowerCase(Locale.ROOT);
            boolean interesting = false;
            for (String keyword : keywords) {
                if (lower.contains(keyword)) {
                    interesting = true;
                    break;
                }
            }
            if (!interesting) {
                continue;
            }
            ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(data.getAddress());
            while (refs.hasNext()) {
                Reference ref = refs.next();
                Function f = fm.getFunctionContaining(ref.getFromAddress());
                if (f == null || !callers.contains(f.getEntryPoint())) {
                    continue;
                }
                matches.computeIfAbsent(f.getEntryPoint(), k -> new ArrayList<>())
                    .add(data.getAddress() + "=" + stringValue);
            }
        }

        List<Address> entries = new ArrayList<>(matches.keySet());
        Collections.sort(entries);
        for (Address entry : entries) {
            Function f = fm.getFunctionAt(entry);
            println("MATCH " + entry + " " + (f == null ? "<none>" : f.getName()));
            List<String> values = matches.get(entry);
            Collections.sort(values);
            for (String value : values) {
                println("  STRING " + value);
            }
        }
        println("MATCHED_CALLERS " + entries.size());
    }
}
