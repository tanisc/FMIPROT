# TM35FIN.py
#
# convert WGS84 (or other) lat/lon to ETRS-TM35FIN
# and figure out their TM35 map tiles
# 
# 2012-2014 Lauri Kangas
# License: ICCLEIYSIUYA (http://evvk.com/evvktvh.html)

import numpy

#      ['L4', 'L4L', 'L41', 'L41L', 'L411', 'L411R', 'L4113', 'L4131R', 'L4113H', 'L4113H3']

# list for using row letters as calculatable indices
rows200 = ['K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X']

# tile sizes indexed by printed map scale (e.g. 1:200k)
size = { 200 : (192000, 96000),
         100 : (96000, 48000),
          50 : (48000, 24000),
          25 : (24000, 12000),
          20 : (12000, 12000),
          10 : (6000, 6000),
           5 : (3000, 3000)}

# tile sizes with list index corresponding to tile level (0..9)
size_level = [ (192000, 96000), 
               (96000, 96000),
               (96000, 48000),
               (48000, 48000),
               (48000, 24000),
               (24000, 24000),
               (24000, 12000),
               (12000, 12000),
               (6000, 6000),
               (3000, 3000)]


grid4 = (('1','2'),('3','4'))
grid8 = (('A','B'), ('C','D'),('E','F'),('G','H'))

K4pos = (500000,6570000) # position of lower right of K4 as reference
refpos = (K4pos[0]-5*size[200][0], K4pos[1]) # "K0" lower left

def latlon_to_xy(lat, lon, src='epsg:4326'):
    import pyproj
    # in:  lat,lon as numpy arrays (dd.dddd, WGS84 default)
    # out: x,y as numpy arrays (ETRS-TM35FIN)

    proj_latlon = pyproj.Proj(init=src) # default: WGS84
    proj_etrs = pyproj.Proj(init='epsg:3067') # ETRS-TM35FIN
    
    return pyproj.transform(proj_latlon, proj_etrs, lon, lat)


def xy_to_latlon(x, y, dst='epsg:4326'):
    # in:  x,y as numpy arrays (ETRS-TM35FIN)
    # out: lat,lon as numpy arrays (dd.ddd, WGS84 default)
    #      (might also be lon,lat...)
    import pyproj

    proj_latlon = pyproj.Proj(init=src) # default: WGS84
    proj_etrs = pyproj.Proj(init='epsg:3067') # ETRS-TM35FIN

    return pyproj.transform(proj_etrs, proj_latlon, x, y)


def tile_of_latlon(lat, lon, level=9, uniq=True, src='epsg:4326'):
    # in:  lat,lon as numpy arrays (dd.dddd, WGS84 default)
    # out: python list of TM35 map tiles

    x, y = latlon_to_xy(lat, lon, src)
    return tile_of_xy(x, y, level=level, uniq=uniq)


def tile_of_xy(x, y, level=9, uniq=True):
    # in:  x,y as numpy arrays (ETRS-TM35FIN)
    # out: python list of TM35 map tiles
    # 
    # calculates full level 9 tile for every (x,y)
    # returns list of shorten()'ed names if level < 9, 
    # non-unique (one for every (x,y)) if uniq=False

    Ndist = (y - refpos[1])
    Edist = (x - refpos[0])

    N200 = divmod(Ndist, size[200][1])
    E200 = divmod(Edist, size[200][0])

    N100 = divmod(N200[1], size[100][1])
    E100 = divmod(E200[1], size[100][0])

    N50 = divmod(N100[1], size[50][1])
    E50 = divmod(E100[1], size[50][0])

    N25 = divmod(N50[1], size[25][1])
    E25 = divmod(E50[1], size[25][0])

    N10 = divmod(N25[1], size[10][1])
    E10 = divmod(E25[1], size[10][0])

    N5 = divmod(N10[1], size[5][1])
    E5 = divmod(E10[1], size[5][0])

    # i've no idea anymore what this does
    tile_parts = numpy.array([[rows200[int(N)] for N in N200[0]],
        ["%d" % E for E in E200[0]],
        [grid4[int(E)][int(N)] for N,E in zip(N100[0],E100[0])],
        [grid4[int(E)][int(N)] for N,E in zip(N50[0], E50[0] )],
        [grid4[int(E)][int(N)] for N,E in zip(N25[0], E25[0] )],
        [grid8[int(E)][int(N)] for N,E in zip(N10[0], E10[0] )],
        [grid4[int(E)][int(N)] for N,E in zip(N5[0],  E5[0]  )]]).T

    if level == 9:
        tiles = [''.join(t) for t in tile_parts]
    else:
        tiles = [shorten(''.join(t))[level] for t in tile_parts]

    if uniq:
        return uniqs(tiles)
    else:
        return tiles

def xy_of_tile(tile, corner='sw'):
    # in:  tile name, e.g. 'L4131F'
    #      corner of coordinate, any of these
    #
    #      ul u ur         nw n ne
    #       l c r     or    w 0 e
    #      ll d lr         sw s se
    #
    # out: (x,y) coordinates within tile (center or upper left)
    #      None for broken tile

    level = tile_level(tile)
    if level < 0:
        return None

    # now we know len(tile) is within 2..7
    row200_letter = tile[0]
    row200_number = rows200.index(row200_letter)
    column200_number = tile[1]
    
    x,y = refpos # lower left of "K0"

    y += row200_number * size[200][1]
    x += int(column200_number) * size[200][0]

    if len(tile) > 2:
        if tile[2] in '34R':
            x += size[100][0]
        if tile[2] in '24':
            y += size[100][1]

    if len(tile) > 3:
        if tile[3] in '34R':
            x += size[50][0]
        if tile[3] in '24':
            y += size[50][1]

    if len(tile) > 4:
        if tile[4] in '34R':
            x += size[25][0]
        if tile[4] in '24':
            y += size[25][1]
    
    if len(tile) > 5:
        offset = 0
        if tile[5] in 'CD':
            offset = 1
        if tile[5] in 'EFR':
            offset = 2
        if tile[5] in 'GH':
            offset = 3
        x += size[10][0]*offset
        if tile[5] in 'BDFH':
            y += size[10][1]

    if len(tile) == 7:
        if tile[6] in '34':
            x += size[5][0]
        if tile[6] in '24':
            y += size[5][1]

    # now x,y points to lower left of tile

    if corner in ['ll','l','ul','sw','w','nw']:
        x_offset = 0

    if corner in ['u','c','d','n','0','s']:
        x_offset = 0.5

    if corner in ['lr','r','ur','se','e','ne']:
        x_offset = 1

    if corner in ['ll','d','lr','sw','s','se']:
        y_offset = 0

    if corner in ['l','c','r','w','0','e']:
        y_offset = 0.5

    if corner in ['ul','u','ur','nw','n','ne']:
        y_offset = 1

    x += size_level[level][0]*x_offset
    y += size_level[level][1]*y_offset

    return x,y

def tile_size(tile):
    # in:  tile name, e.g. 'L4131E'
    # out: tile size in meters, e.g. (6000, 6000), None if broken tile

    level = tile_level(tile)

    if level < 0:
        return None

    return size_level[level]

def tile_level(tile):
    # in:  tile name, e.g. 'L4131E'
    # out: tile level index (0..9), -1 if broken name
    
    if len(tile) < 2 or len(tile) > 7:
        return -1
    
    legal = ['KLMNPQRSTUVWX', '23456', '1234', '1234', '1234', 'ABCDEFGH', '1234']
    
    LR = False
    if tile[-1] in 'LR':
        if len(tile) == 7:
            return -1 # e.g. L4131AR illegal
        LR = True
        tile = tile[:-1]

    

    # possible level based on tile length, corrected later for LR tiles
    levels = [-1, -1, 0, 2, 4, 6, 8, 9]
    

    for i,c in enumerate(tile):
        if not c in legal[i]:
            return -1

    level = levels[len(tile)]

    if LR:
        level += 1

    return level

def shorten(tile):
    # in:  tile name, e.g. 
    #      'L4113H3'
    # out: list of shortened tile names, with L&R, e.g.
    #      ['L4', 'L4L', 'L41', 'L41L', 'L411', 'L411R', 'L4113', 'L4131R', 'L4113H', 'L4113H3']

    shortened_tiles = [tile[0:c+2] for c in range(len(tile)-1)] 

    LRtiles = [t[:-1]+('L' if t[-1] in '12' else 'R') for t in shortened_tiles[1:4]]

    for LR,k in zip(LRtiles, [1,3,5]):
        shortened_tiles.insert(k, LR)

    t = shortened_tiles[7]

    shortened_tiles.insert(7, t[:-1] + ('L' if t[-1] in 'ABCD' else 'R'))

    return shortened_tiles



# pick unique values from list, preserve order
def uniqs(seq, idfun=None): 
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result
