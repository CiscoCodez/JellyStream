root@zero0xypher:/home/ubuntu# cat "/media/jellyfin/serienstream/(Un)Well/Season 01/S01E01.strm"
http://localhost:3000/stream/redirect/8888011root@zero0xypher:/home/ubuntu#
root@zero0xypher:/home/ubuntu# curl -I "http://localhost:3000/stream/redirect/8888011"
curl "http://localhost:3000/stream/redirect/8888011" | head
HTTP/1.1 500 INTERNAL SERVER ERROR
Server: gunicorn
Date: Fri, 20 Mar 2026 22:23:27 GMT
Connection: close
Content-Type: application/json
Content-Length: 34

  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    34  100    34    0     0  10859      0 --:--:-- --:--:-- --:--:-- 11333
{"error":"Internal server error"}
root@zero0xypher:/home/ubuntu# systemctl status jellystream-api.service
● jellystream-api.service - JellyStream API
     Loaded: loaded (/etc/systemd/system/jellystream-api.service; enabled; preset: enabled)
     Active: active (running) since Fri 2026-03-20 16:52:33 UTC; 5h 31min ago
   Main PID: 351823 (gunicorn)
      Tasks: 5 (limit: 28690)
     Memory: 123.1M (peak: 123.4M)
        CPU: 3.739s
     CGroup: /system.slice/jellystream-api.service
             ├─351823 /usr/bin/python3 /usr/bin/gunicorn -w 4 -b 0.0.0.0:3000 --chdir /home/ubuntu/JellyStream/api main:app
             ├─351826 /usr/bin/python3 /usr/bin/gunicorn -w 4 -b 0.0.0.0:3000 --chdir /home/ubuntu/JellyStream/api main:app
             ├─351827 /usr/bin/python3 /usr/bin/gunicorn -w 4 -b 0.0.0.0:3000 --chdir /home/ubuntu/JellyStream/api main:app
             ├─351828 /usr/bin/python3 /usr/bin/gunicorn -w 4 -b 0.0.0.0:3000 --chdir /home/ubuntu/JellyStream/api main:app
             └─351829 /usr/bin/python3 /usr/bin/gunicorn -w 4 -b 0.0.0.0:3000 --chdir /home/ubuntu/JellyStream/api main:app

Mar 20 22:23:17 zero0xypher gunicorn[351829]: 2026-03-20 22:23:17,684 - ERROR - ❌ Error resolving redirect 8888011: 'NoneType' object has no attribute 'find_episode_by_re>
Mar 20 22:23:17 zero0xypher gunicorn[351827]: 2026-03-20 22:23:17,784 - INFO - 🎬 Stream request for redirect 8888011
Mar 20 22:23:17 zero0xypher gunicorn[351827]: 2026-03-20 22:23:17,784 - INFO - 🔍 No cache found for 8888011, resolving fresh...
Mar 20 22:23:17 zero0xypher gunicorn[351827]: 2026-03-20 22:23:17,784 - ERROR - ❌ Error resolving redirect 8888011: 'NoneType' object has no attribute 'find_episode_by_re>
Mar 20 22:23:27 zero0xypher gunicorn[351828]: 2026-03-20 22:23:27,675 - INFO - 🎬 Stream request for redirect 8888011
Mar 20 22:23:27 zero0xypher gunicorn[351828]: 2026-03-20 22:23:27,675 - INFO - 🔍 No cache found for 8888011, resolving fresh...
Mar 20 22:23:27 zero0xypher gunicorn[351828]: 2026-03-20 22:23:27,675 - ERROR - ❌ Error resolving redirect 8888011: 'NoneType' object has no attribute 'find_episode_by_re>
Mar 20 22:23:27 zero0xypher gunicorn[351826]: 2026-03-20 22:23:27,688 - INFO - 🎬 Stream request for redirect 8888011
Mar 20 22:23:27 zero0xypher gunicorn[351826]: 2026-03-20 22:23:27,689 - INFO - 🔍 No cache found for 8888011, resolving fresh...
Mar 20 22:23:27 zero0xypher gunicorn[351826]: 2026-03-20 22:23:27,689 - ERROR - ❌ Error resolving redirect 8888011: 'NoneType' object has no attribute 'find_episode_by_re>
lines 1-24/24 (END)
