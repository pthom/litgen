import lg_mylib


def test_make_shared_elem():
    elem = lg_mylib.make_shared_elem(3)
    assert elem.x == 3


def test_elem_container():
    container = lg_mylib.ElemContainer()

    assert len(container.vec) == 2
    assert container.vec[0].x == 1

    assert container.shared_ptr is not None
    assert container.shared_ptr.x == 3

    assert len(container.vec_shared_ptrs) == 2
    assert container.vec_shared_ptrs[0].x == 4
