from zk import ZK, const

# Ganti dengan IP dan port mesin fingerprint Anda
zk = ZK('10.10.2.173', port=4370, timeout=5)

try:
    conn = zk.connect()
    print("✅ Berhasil konek ke mesin!")
    print("Model:", conn.get_device_name())
    print("Jumlah user:", len(conn.get_users()))
    print("Jumlah attendance log:", len(conn.get_attendance()))
    conn.disconnect()
except Exception as e:
    print("❌ Gagal konek:", e)
