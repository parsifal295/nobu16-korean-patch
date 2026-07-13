// Dump 64-bit pointer tables at one or more addresses.
// @category NOBU16

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

public class DumpPointerTable extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length == 0) throw new IllegalArgumentException("address [count]");
        Address base = currentProgram.getAddressFactory().getAddress(args[0]);
        int count = args.length > 1 ? Integer.decode(args[1]) : 16;
        for (int i = 0; i < count; i++) {
            Address slot = base.add(i * 8L);
            long value = getLong(slot);
            Address target = currentProgram.getAddressFactory().getAddress(Long.toUnsignedString(value, 16));
            Function f = getFunctionAt(target);
            println(String.format("%s +0x%x = %s %s", base, i * 8, target,
                f == null ? "" : f.getName()));
        }
    }
}
