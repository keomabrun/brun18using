def test_mac_to_id():
    import tools
    mote_id     = 6
    mote_mac    = "00-17-0d-00-00-3f-fe-87"
    assert mote_id == tools.mac_to_id(mote_mac,1461282879)

def test_id_to_mac():
    import tools
    mote_id     = 4
    mote_mac    = "00-17-0d-00-00-3f-fe-87"
    assert (mote_mac,None) == tools.id_to_mac(mote_id,1466218844, True)
    assert tools.id_to_mac(mote_id,1460282879) is None
