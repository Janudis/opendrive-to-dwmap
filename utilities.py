import numpy as np
import pyproj

# connect to local transformation
def rigid_transform_3D(A, B):
    assert A.shape == B.shape

    num_rows, num_cols = A.shape
    if num_rows != 3:
        raise Exception(f"matrix A is not 3xN, it is {num_rows}x{num_cols}")

    num_rows, num_cols = B.shape
    if num_rows != 3:
        raise Exception(f"matrix B is not 3xN, it is {num_rows}x{num_cols}")

    # find mean column wise
    centroid_A = np.mean(A, axis=1)
    centroid_B = np.mean(B, axis=1)

    # ensure centroids are 3x1
    centroid_A = centroid_A.reshape(-1, 1)
    centroid_B = centroid_B.reshape(-1, 1)

    # subtract mean
    Am = A - centroid_A
    Bm = B - centroid_B

    H = Am @ np.transpose(Bm)

    # sanity check
    #if linalg.matrix_rank(H) < 3:
    #    raise ValueError("rank of H = {}, expecting 3".format(linalg.matrix_rank(H)))

    # find rotation
    U, S, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T

    # special reflection case
    if np.linalg.det(R) < 0:
        print("det(R) < R, reflection detected!, correcting for it ...")
        Vt[2,:] *= -1
        R = Vt.T @ U.T

    t = -R @ centroid_A + centroid_B

    return R, t

# transformation from wgs84 to the local coordinate system of dw maps
def transform_wgs84_to_local(lon, lat, z, origin_lon, origin_lat, origin_z):

    transformation_string = "+proj=tmerc +lon_0=" +str(origin_lon)+ " +lat_0=" +str(origin_lat)+ " +k=1 +x_0=0 +y_0=0 +ellps=WGS84 +units=m +no_defs"
    p = pyproj.Proj(transformation_string)

    x, y = p(lon, lat)

    z = 0

    return x, y, z

def geodetic_to_cartesian(x, y, z):
    geod_to_cart = pyproj.Transformer.from_crs(
        {"proj":'latlong', "ellps":'WGS84', "datum":'WGS84'},
        {"proj":'geocent', "ellps":'WGS84', "datum":'WGS84'},
    )

    x, y, z = geod_to_cart.transform(x, y, z, radians=False)

    return(x, y, z)

def cartesian_to_geodetic(x, y, z):
    cart_to_geod = pyproj.Transformer.from_crs(
        {"proj":'geocent', "ellps":'WGS84', "datum":'WGS84'},
        {"proj":'latlong', "ellps":'WGS84', "datum":'WGS84'},
    )

    x, y, z = cartesian_to_geodetic.transform(x, y, z, radians=False)

    return(x, y, z)


# b = np.array([[40.5150190345588], [22.99331428829945], [0]])
# # print(a.shape)
# a = np.array([[40.51508930502561], [22.993284708827595], [0]])
# x = rigid_transform_3D(a, b)
# print(x)

from pyproj import CRS, Transformer
import numpy as np
import simil

def local_to_wgs84(geodet_ctrl_p, local_ctrl_p, local_other_p): #https://gis.stackexchange.com/questions/386393/convert-x-y-z-local-points-to-wgs84-having-only-3-coordinates-known
    # CRSes definitions
    geodet_crs = CRS.from_epsg(4979) # Geodetic (lat,lon,h) system
    geocent_crs = CRS.from_epsg(4978) # Geocentric (X,Y,Z) system
    
    # pyproj transformer object from geodetic to geocentric
    geodet_to_geocent = Transformer.from_crs(geodet_crs ,geocent_crs)
    
    # convert geodetic control points to geocentric
    geocent_ctrl_p = [geodet_to_geocent.transform(p[0],p[1],p[2])
                      for p in geodet_ctrl_p]
    
    m_scalar, r_matrix, t_vector = simil.process(local_ctrl_p,
                                             geocent_ctrl_p,
                                             scale=False,
                                             lambda_0=1)
    #print('M scalar = ', m_scalar)
    #print('R Matrix = \n', r_matrix)
    #print('T Vector = \n',  t_vector)
    
    local_ctrl_coords = np.array(local_ctrl_p).T 
    # transform the control coordinates
    transf_ctrl_coords = m_scalar * r_matrix @ local_ctrl_coords + t_vector
    
    # transpose transformed control coordinates to get points
    transf_ctrl_p = transf_ctrl_coords.T
    local_other_coords = np.array(local_other_p).T
    transf_other_coords = m_scalar * r_matrix @ local_other_coords + t_vector
    transf_other_p = transf_other_coords.T 
    # convert other points to geodetic
    geocent_to_geodet = Transformer.from_crs(geocent_crs ,geodet_crs)
    geodet_other_p = [geocent_to_geodet.transform(p[0],p[1],p[2])
                      for p in transf_other_p]
    
    return(np.array(geodet_other_p))
