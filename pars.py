ips = """  TCP    0.0.0.0:135            0.0.0.0:0              LISTENING       776
  TCP    0.0.0.0:445            0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:902            0.0.0.0:0              LISTENING       3868
  TCP    0.0.0.0:912            0.0.0.0:0              LISTENING       3868
  TCP    0.0.0.0:1947           0.0.0.0:0              LISTENING       3832
  TCP    0.0.0.0:3185           0.0.0.0:0              LISTENING       3480
  TCP    0.0.0.0:3186           0.0.0.0:0              LISTENING       3480
  TCP    0.0.0.0:3187           0.0.0.0:0              LISTENING       3480
  TCP    0.0.0.0:5040           0.0.0.0:0              LISTENING       5612
  TCP    0.0.0.0:5432           0.0.0.0:0              LISTENING       4912
  TCP    0.0.0.0:7070           0.0.0.0:0              LISTENING       3408
  TCP    0.0.0.0:8090           0.0.0.0:0              LISTENING       8820
  TCP    0.0.0.0:22350          0.0.0.0:0              LISTENING       4056
  TCP    0.0.0.0:22352          0.0.0.0:0              LISTENING       3372
  TCP    0.0.0.0:27080          0.0.0.0:0              LISTENING       4804
  TCP    0.0.0.0:49664          0.0.0.0:0              LISTENING       876
  TCP    0.0.0.0:49665          0.0.0.0:0              LISTENING       708
  TCP    0.0.0.0:49666          0.0.0.0:0              LISTENING       1444
  TCP    0.0.0.0:49667          0.0.0.0:0              LISTENING       1704
  TCP    0.0.0.0:49668          0.0.0.0:0              LISTENING       3044
  TCP    0.0.0.0:49677          0.0.0.0:0              LISTENING       848
  TCP    0.0.0.0:55259          0.0.0.0:0              LISTENING       13024
  TCP    127.0.0.1:8000         0.0.0.0:0              LISTENING       8572
  TCP    127.0.0.1:28385        0.0.0.0:0              LISTENING       4
  TCP    127.0.0.1:28390        0.0.0.0:0              LISTENING       4
  TCP    127.0.0.1:49350        0.0.0.0:0              LISTENING       15332
  TCP    127.0.0.1:49351        0.0.0.0:0              LISTENING       7076
  TCP    127.0.0.1:51283        0.0.0.0:0              LISTENING       3664
  TCP    127.0.0.1:63342        0.0.0.0:0              LISTENING       14396
  TCP    172.23.176.1:139       0.0.0.0:0              LISTENING       4
  TCP    192.168.0.10:139       0.0.0.0:0              LISTENING       4
  TCP    192.168.80.1:139       0.0.0.0:0              LISTENING       4
  TCP    192.168.159.1:139      0.0.0.0:0              LISTENING       4
  TCP    [::]:135               [::]:0                 LISTENING       776
  TCP    [::]:445               [::]:0                 LISTENING       4
  TCP    [::]:1947              [::]:0                 LISTENING       3832
  TCP    [::]:3185              [::]:0                 LISTENING       3480
  TCP    [::]:3186              [::]:0                 LISTENING       3480
  TCP    [::]:3187              [::]:0                 LISTENING       3480
  TCP    [::]:5432              [::]:0                 LISTENING       4912
  TCP    [::]:7070              [::]:0                 LISTENING       3408
  TCP    [::]:22350             [::]:0                 LISTENING       4056
  TCP    [::]:22352             [::]:0                 LISTENING       3372
  TCP    [::]:27080             [::]:0                 LISTENING       4804
  TCP    [::]:49664             [::]:0                 LISTENING       876
  TCP    [::]:49665             [::]:0                 LISTENING       708
  TCP    [::]:49666             [::]:0                 LISTENING       1444
  TCP    [::]:49667             [::]:0                 LISTENING       1704
  TCP    [::]:49668             [::]:0                 LISTENING       3044
  TCP    [::]:49677             [::]:0                 LISTENING       848
  TCP    [::]:55259             [::]:0                 LISTENING       13024"""

data = ips.split()
# print(data)
set_data = set()
for i in range(0, len(data), 5):
    print(i)
    line = data[i:i+5]
    print(line)
    set_data.add(line[-1])
    print('-----')

data = sorted(map(int, set_data))
for process in data:
    print(f'tasklist | findstr {process}')
    