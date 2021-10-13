import numpy as np
import pytest
from pyaerocom.exceptions import MetaDataError, UnitConversionError, \
    DataUnitError, CoordinateError
from pyaerocom import stationdata as mod
from pyaerocom.io import ReadEarlinet
from .conftest import FAKE_STATION_DATA, does_not_raise_exception

def get_aeronet_site(aeronetsunv3lev2_subset, index, var_name):
    return aeronetsunv3lev2_subset.to_station_data(index,
                                                   vars_to_convert=var_name)

def get_earlinet_data(var_name):
    data = ReadEarlinet('Earlinet-test').read(vars_to_retrieve=var_name)
    stats = data.to_station_data_all()['stats']
    assert len(stats) == 1
    return stats[0]

stat1 = FAKE_STATION_DATA['station_data1']
stat2 = FAKE_STATION_DATA['station_data2']

def test_StationData_copy():
    cp = stat1.copy()
    for key, val in stat1.items():
        assert key in cp
        if isinstance(val, np.ndarray):
            assert np.all(val == cp[key])
        else:
            assert val == cp[key]

stat3 = stat2.copy()
stat3['concno2'] = np.ones(10)
stat3['var_info']['concno2'] = dict(unit='ug m-3')
stat3['concso4'] = np.ones(10)
stat3['var_info']['concso4'] = dict(units='1')
stat3['ts_type'] = None
stat3['station_coords']['latitude'] = 'blaaa'
stat4 = stat2.copy()
stat4['longitude'] = '42'

ec_earlinet = get_earlinet_data('ec532aer')

def test_StationData_default_vert_grid():
    grid = stat1.default_vert_grid
    assert grid.mean() == 7375 #m
    step = np.unique(np.diff(grid))
    assert len(step) == 1
    assert step[0] == 250

def test_StationData_vars_available():
    assert stat1.vars_available == ['ec550aer', 'od550aer']

def test_StationData_has_var():
    assert stat1.has_var('od550aer')
    assert stat2.has_var('conco3')
    assert not stat2.has_var('abs550aer')
    st = stat2.copy()
    st['abs550aer'] = np.ones(10)
    assert st.has_var('abs550aer')

@pytest.mark.parametrize('stat,var_name,val,raises', [
    (stat1, 'ec550aer', 'm-1', does_not_raise_exception()),
    (stat1, 'concco', None, pytest.raises(MetaDataError)),
    (stat3, 'concno2', None, pytest.raises(MetaDataError)),
])
def test_StationData_get_unit(stat,var_name,val,raises):
    with raises:
        assert stat.get_unit(var_name) == val

def test_StationData_units():
    assert stat1.units == {'ec550aer': 'm-1', 'od550aer': '1'}

@pytest.mark.parametrize('stat,var_name,val,raises', [
    (stat1, 'ec550aer', '1/Mm', does_not_raise_exception()),
    (stat1, 'concco', None, pytest.raises(MetaDataError)),
    (stat3, 'concso4', None, pytest.raises(UnitConversionError)),
])
def test_StationData_check_var_unit_aerocom(stat,var_name,val,raises):
    stat = stat.copy()
    with raises:
        stat.check_var_unit_aerocom(var_name)
        assert stat.get_unit(var_name) == val


@pytest.mark.parametrize('stat,var_name,unit,raises', [
    (stat1, 'ec550aer', None, pytest.raises(DataUnitError)),
    (stat1, 'ec550aer', 'm-1', does_not_raise_exception()),
])
def test_StationData_check_unit(stat,var_name,unit,raises):
    with raises:
        stat.check_unit(var_name,unit)

@pytest.mark.parametrize('stat,var_name,to_unit,raises', [
    (stat1, 'ec550aer', '1/Gm', does_not_raise_exception()),
    (stat3, 'concso4', 'kg m-3', pytest.raises(UnitConversionError)),
])
def test_StationData_convert_unit(stat,var_name,to_unit,raises):
    with raises:
        stat.convert_unit(var_name,to_unit)

def test_StationData_dist_other():
    dist = stat1.dist_other(stat2)
    np.testing.assert_allclose(dist, 1.11, atol=0.1)

@pytest.mark.parametrize('stat,other,tol_km,result', [
    (stat1,stat1,None,True),
    (stat1,stat2,1,False),
    (stat1,stat2,2,True),

])
def test_StationData_same_coords(stat,other,tol_km,result):
    assert stat.same_coords(other, tol_km) == result

@pytest.mark.parametrize('stat,force_single_value,dtype,raises', [
    (mod.StationData(), False, None, does_not_raise_exception()),
    (stat1, False, None, does_not_raise_exception()),
    (stat1, True, float, does_not_raise_exception()),
    (stat2,True,float, does_not_raise_exception()),
    (stat3, True, float, pytest.raises(MetaDataError)),
    (stat4, True, None, pytest.raises(AttributeError)),
    (mod.StationData(station_coords=dict(
        latitude=42,longitude=42, altitude=42)),
     False, None, does_not_raise_exception()),
    (mod.StationData(latitude=[42,44,32],longitude=42, altitude=42),
     True, None, pytest.raises(ValueError)),

])
def test_StationData_get_station_coords(stat,force_single_value,dtype,raises):
    with raises:
        coords = stat.get_station_coords(force_single_value=force_single_value)
        assert isinstance(coords, dict)
        if dtype is not None:
            for val in coords.values():
                assert isinstance(val,dtype)

@pytest.mark.parametrize('stat,force_single_value,quality_check,'
                         'add_none_vals,add_meta_keys,numitems,raises', [
    (stat1,True,True,False,None, 14,does_not_raise_exception()),
    (stat1,True,True,False,'blaaa', 14,does_not_raise_exception()),
    (stat1,True,True,False,['random_key1','random_key2'], 16,
     does_not_raise_exception()),
    (stat1,True,True,False,['random_key3'], None,pytest.raises(MetaDataError)),
    (stat1,True,True,False,['random_key4'], 15, does_not_raise_exception()),
    (stat1,True,True,True,['random_key4'], 23, does_not_raise_exception()),
])
def test_StationData_get_meta(stat,force_single_value,quality_check,
                              add_none_vals,
                              add_meta_keys,numitems,raises):
    with raises:
        meta = stat.get_meta(force_single_value,quality_check,add_none_vals,
                             add_meta_keys)
        assert isinstance(meta, dict)
        assert len(meta) == numitems

@pytest.mark.parametrize('stat,key,raises', [
    (stat1, 'station_name', does_not_raise_exception()),
    (stat1, 'framework', does_not_raise_exception()),
    (stat1, 'longitude', does_not_raise_exception()),
])
def test_StationData__check_meta_item(stat,key,raises):
    with raises:
        stat.copy()._check_meta_item(key)

@pytest.mark.parametrize('stat,other,coord_tol_km,check_coords,inplace,'
                         'add_meta_keys,raise_on_error,raises', [
    (stat1, stat1,0.1,True,True,None,True,does_not_raise_exception()),
    (stat1, stat2,0.001,True,True,None,True,pytest.raises(CoordinateError)),
    (stat1, stat2,50,True,True,None,True,does_not_raise_exception()),
    (stat1, stat2,50,True,True,['random_key1'],True,does_not_raise_exception()),
    (stat1, stat2,50,True,False,['random_key1'],True,
     does_not_raise_exception()),
])
def test_StationData_merge_meta_same_station(stat,other,coord_tol_km,
                                             check_coords,inplace,
                                             add_meta_keys,raise_on_error,
                                             raises):
    with raises:
        stat=stat.copy()
        val = stat.merge_meta_same_station(other.copy(),coord_tol_km,
                                            check_coords,inplace,add_meta_keys,
                                            raise_on_error)
        assert isinstance(val, mod.StationData)
        if inplace:
            assert val is stat
        else:
            assert val is not stat

@pytest.mark.parametrize('stat,other,var_name,raises',[
    (stat1, stat1, 'ec550aer', does_not_raise_exception()),
    (stat1, stat2, 'ec550aer', does_not_raise_exception()),
    (stat1, stat2, 'conco3', pytest.raises(MetaDataError)),
    (stat2, stat1, 'conco3', pytest.raises(MetaDataError)),
])
def test_StationData_merge_varinfo(stat,other,var_name,raises):
    with raises:
        val = stat.merge_varinfo(other,var_name)
        assert isinstance(val, mod.StationData)

@pytest.mark.parametrize('stat,var_name,val', [
    (stat1, 'od550aer', False),
    (ec_earlinet, 'ec532aer', True),
])
def test_StationData_check_if_3d(stat,var_name,val):
    assert stat.check_if_3d(var_name) == val

def test_StationData___str__():
    assert isinstance(str(stat1), str)