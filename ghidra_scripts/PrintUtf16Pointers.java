// @category NOBU16
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;

public class PrintUtf16Pointers extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) {
            throw new IllegalArgumentException("base [count]");
        }
        Address base = currentProgram.getAddressFactory().getAddress(args[0]);
        int count = args.length > 1 ? Integer.decode(args[1]) : 16;
        for (int i = 0; i < count; i++) {
            Address slot = base.add(i * 8L);
            long raw = getLong(slot);
            Address target = currentProgram.getAddressFactory().getAddress(Long.toUnsignedString(raw, 16));
            StringBuilder value = new StringBuilder();
            try {
                for (int j = 0; j < 512; j++) {
                    int ch = getShort(target.add(j * 2L)) & 0xffff;
                    if (ch == 0) {
                        break;
                    }
                    value.append((char)ch);
                }
            } catch (Exception e) {
                value.append("<unreadable>");
            }
            println(String.format("%s +0x%x -> %s %s", base, i * 8, target, value.toString()));
        }
    }
}
