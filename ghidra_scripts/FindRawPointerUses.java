// Find raw little-endian 64-bit VAs and 32-bit RVAs that point at target addresses.
// This is useful for reflection/registration tables that Ghidra has not typed.
// @category NOBU16

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.Memory;

public class FindRawPointerUses extends GhidraScript {
    private byte[] littleEndian(long value, int size) {
        byte[] out = new byte[size];
        for (int i = 0; i < size; i++) {
            out[i] = (byte)((value >>> (i * 8)) & 0xff);
        }
        return out;
    }

    private void findAll(Memory memory, byte[] needle, String kind, Address target) throws Exception {
        Address cursor = memory.getMinAddress();
        while (cursor != null && cursor.compareTo(memory.getMaxAddress()) <= 0) {
            Address hit = memory.findBytes(cursor, memory.getMaxAddress(), needle, null, true, monitor);
            if (hit == null) break;
            Function f = getFunctionContaining(hit);
            println("  " + kind + " " + hit + " " +
                (f == null ? "<no-function>" : f.getName() + "@" + f.getEntryPoint()));
            cursor = hit.add(1);
        }
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length == 0) throw new IllegalArgumentException("target address required");
        Memory memory = currentProgram.getMemory();
        long imageBase = currentProgram.getImageBase().getOffset();
        for (String arg : args) {
            Address target = currentProgram.getAddressFactory().getAddress(arg);
            long va = target.getOffset();
            long rva = va - imageBase;
            println("TARGET " + target + " RVA 0x" + Long.toHexString(rva));
            findAll(memory, littleEndian(va, 8), "VA64", target);
            findAll(memory, littleEndian(rva, 4), "RVA32", target);
        }
    }
}
