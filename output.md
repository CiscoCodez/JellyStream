root@zero0xypher:/home/ubuntu# curl http://localhost:3000/test/8888011
curl -I http://localhost:3000/stream/redirect/8888011
curl http://localhost:3000/stream/redirect/8888011 | head
{"extraction_method":"voe_provider","provider_type":"voe","provider_url":"https://dianaavoidthey.com/e/yc1v0a66y4d2","redirect_id":"8888011","redirect_url":"https://serienstream.to/r?t=eyJpdiI6IktSeXR2RUZVT1pZTnBmNnp0QTRTdmc9PSIsInZhbHVlIjoiWWNRTGxVUE10Q0o0K1VlWDR0Sm9QL09uVTBZVzZVK24wQWFmOWtkTG5sUWR1VmU3Q0NGQ1g5djE0TlRTZW9JaG5JakFqMk9xM2hPMktiNUFNNjRnZXc9PSIsIm1hYyI6IjhlMjBlYzU3NGZkYWRiOTRlMDYwYWE2N2NiYzY2ODJhNDBmYzAyMDdmMzJiODBlNzM4MWEzZjA1M2UyZDZiN2YiLCJ0YWciOiIifQ%3D%3D","stream_url":"https://cdn-xhcgna8lhaqar6c1.edgeon-bandwidth.com/engine/hls2/01/00922/yc1v0a66y4d2_,n,.urlset/master.m3u8?t=53X52dFwlwK89y9OZRxaNVy-VZz3TLeRzd1b6n4Fxt4&s=1774052069&e=14400&f=4613724&node=IKNX1MQTh+SIaOwf+T9siRws72RJxHipotvUtq+AZlM=&i=193.122&sp=2500&asn=31898&q=n&rq=8IhixgDVJHkF7BlEmZmRVlpADgw9b7Wkv6MzVuWC"}
HTTP/1.1 200 OK
Server: gunicorn
Date: Sat, 21 Mar 2026 00:14:29 GMT
Connection: close
Content-Type: application/vnd.apple.mpegurl
Access-Control-Allow-Origin: *
Cache-Control: no-cache
Content-Length: 754

  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   756  100   756    0     0   1063      0 --:--:-- --:--:-- --:--:--  1061
#EXTM3U
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1542209,RESOLUTION=1280x720,FRAME-RATE=30.000,CODECS="avc1.64001f,mp4a.40.2"
https://cdn-qkvhbkc92hdjoa6i.edgeon-bandwidth.com/engine/hls2-c/01/00922/yc1v0a66y4d2_,n,.urlset/index-v1-a1.m3u8?t=SXpIl4jEGDQ3o9wMMuch94umNi0S3q01o6ToXqi8FTw&s=1774052070&e=14400&f=4613724&node=IKNX1MQTh+SIaOwf+T9siRws72RJxHipotvUtq+AZlM=&i=193.122&sp=2500&asn=31898&q=n&rq=qON2vyGeGrkSJ043Aci4pDHSCNGJxTGIn0lb9eYs

#EXT-X-I-FRAME-STREAM-INF:BANDWIDTH=147465,RESOLUTION=1280x720,CODECS="avc1.64001f",URI="iframes-v1-a1.m3u8?t=SXpIl4jEGDQ3o9wMMuch94umNi0S3q01o6ToXqi8FTw&s=1774052070&e=14400&f=4613724&node=IKNX1MQTh+SIaOwf+T9siRws72RJxHipotvUtq+AZlM=&i=193.122&sp=2500&asn=31898&q=n&rq=qON2vyGeGrkSJ043Aci4pDHSCNGJxTGIn0lb9eYs"
root@zero0xypher:/home/ubuntu# sudo systemctl status jellystream-api.service
● jellystream-api.service - JellyStream API
     Loaded: loaded (/etc/systemd/system/jellystream-api.service; enabled; preset: enabled)
     Active: active (running) since Sat 2026-03-21 00:14:23 UTC; 1min 3s ago
   Main PID: 464520 (gunicorn)
      Tasks: 5 (limit: 28690)
     Memory: 1.1G (peak: 1.8G)
        CPU: 9.520s
     CGroup: /system.slice/jellystream-api.service
             ├─464520 /usr/bin/python3 /usr/bin/gunicorn -w 4 -b 0.0.0.0:3000 --chdir /home/ubuntu/JellyStream/api main:app
             ├─464525 /usr/bin/python3 /usr/bin/gunicorn -w 4 -b 0.0.0.0:3000 --chdir /home/ubuntu/JellyStream/api main:app
             ├─464526 /usr/bin/python3 /usr/bin/gunicorn -w 4 -b 0.0.0.0:3000 --chdir /home/ubuntu/JellyStream/api main:app
             ├─464527 /usr/bin/python3 /usr/bin/gunicorn -w 4 -b 0.0.0.0:3000 --chdir /home/ubuntu/JellyStream/api main:app
             └─464528 /usr/bin/python3 /usr/bin/gunicorn -w 4 -b 0.0.0.0:3000 --chdir /home/ubuntu/JellyStream/api main:app

Mar 21 00:14:41 zero0xypher gunicorn[464527]: 2026-03-21 00:14:41,065 - INFO - Resolving redirect: https://serienstream.to/r?t=eyJpdiI6Inh0S2RJejRyYk9ISFVvM1hRWnNkRHc9PSIs>
Mar 21 00:14:41 zero0xypher gunicorn[464527]: 2026-03-21 00:14:41,066 - INFO - Step 1: Requesting https://serienstream.to/r?t=eyJpdiI6Inh0S2RJejRyYk9ISFVvM1hRWnNkRHc9PSIsI>
Mar 21 00:14:41 zero0xypher gunicorn[464527]: 2026-03-21 00:14:41,123 - WARNING - Encountered Turnstile challenge page while resolving stream URL
Mar 21 00:14:41 zero0xypher gunicorn[464527]: 2026-03-21 00:14:41,123 - INFO - 🏁 Background season caching completed
Mar 21 00:14:41 zero0xypher gunicorn[464526]: 2026-03-21 00:14:41,653 - INFO - 🔄 Background caching: 13476101
Mar 21 00:14:41 zero0xypher gunicorn[464526]: 2026-03-21 00:14:41,833 - INFO - Refreshed stream URL for 13476101
Mar 21 00:14:41 zero0xypher gunicorn[464526]: 2026-03-21 00:14:41,834 - INFO - Resolving redirect: https://serienstream.to/r?t=eyJpdiI6Inh0S2RJejRyYk9ISFVvM1hRWnNkRHc9PSIs>
Mar 21 00:14:41 zero0xypher gunicorn[464526]: 2026-03-21 00:14:41,835 - INFO - Step 1: Requesting https://serienstream.to/r?t=eyJpdiI6Inh0S2RJejRyYk9ISFVvM1hRWnNkRHc9PSIsI>
Mar 21 00:14:41 zero0xypher gunicorn[464526]: 2026-03-21 00:14:41,890 - WARNING - Encountered Turnstile challenge page while resolving stream URL
Mar 21 00:14:41 zero0xypher gunicorn[464526]: 2026-03-21 00:14:41,890 - INFO - 🏁 Background season caching completed
