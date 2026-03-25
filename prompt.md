 I ran all the commands u provided but couldn't connect to `http://193.122.61.236:6080/vnc.html`

root@zero0xypher:/home/ubuntu/JellyStream/api# ps -ef | grep Xvfb
echo $DISPLAY
root     2316241 2301024  0 17:11 pts/1    00:00:00 Xvfb :99 -screen 0 1440x900x24
root     2316955 2301024  0 17:14 pts/1    00:00:00 grep --color=auto Xvfb
:99
root@zero0xypher:/home/ubuntu/JellyStream/api#

root@zero0xypher:/home/ubuntu/JellyStream/api# export DISPLAY=:99
fluxbox >/tmp/fluxbox.log 2>&1 &
[2] 2317002
root@zero0xypher:/home/ubuntu/JellyStream/api#

root@zero0xypher:/home/ubuntu/JellyStream/api# mkdir -p ~/.vnc
x11vnc -storepasswd
Enter VNC password:
Verify password:
Write password to /root/.vnc/passwd?  [y]/n y
Password written to: /root/.vnc/passwd

root@zero0xypher:/home/ubuntu/JellyStream/api# export DISPLAY=:99
x11vnc -display :99 -forever -shared -rfbauth ~/.vnc/passwd -rfbport 5900 >/tmp/x11vnc.log 2>&1 &
[3] 2317474
root@zero0xypher:/home/ubuntu/JellyStream/api#

root@zero0xypher:/home/ubuntu/JellyStream/api# websockify --web=/usr/share/novnc/ 6080 localhost:5900 >/tmp/novnc.log 2>&1 &
[4] 2317629
root@zero0xypher:/home/ubuntu/JellyStream/api#


root@zero0xypher:/home/ubuntu/JellyStream/api# ls /usr/share/novnc
app  core  include  utils  vendor  vnc.html  vnc_auto.html  vnc_lite.html

root@zero0xypher:/home/ubuntu/JellyStream/api# cd /home/ubuntu/JellyStream/api
DISPLAY=:99 JELLYSTREAM_PLAYWRIGHT_HEADLESS=0 /home/ubuntu/JellyStream/.venv/bin/python -m browser.bootstrap_session
2026-03-25 17:17:00,916 - INFO - Launching persistent Playwright browser (headless=False, profile=/home/ubuntu/JellyStream/api/browser/.playwright-profile)
2026-03-25 17:17:03,030 - INFO - Persistent browser session opened at https://serienstream.to
2026-03-25 17:17:03,030 - INFO - Leave this process running while you complete any Turnstile challenge in the browser session.
2026-03-25 17:17:03,030 - INFO - Press Ctrl+C after the session looks healthy; cookies will stay in the persistent profile.
^C2026-03-25 17:20:25,479 - INFO - Bootstrap session closed by user.
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/home/ubuntu/JellyStream/api/browser/bootstrap_session.py", line 50, in <module>
    sys.exit(main())
             ^^^^^^
  File "/home/ubuntu/JellyStream/api/browser/bootstrap_session.py", line 46, in main
    resolver.close()
  File "/home/ubuntu/JellyStream/api/browser/playwright_resolver.py", line 83, in close
    self._context.close()
  File "/home/ubuntu/JellyStream/.venv/lib/python3.12/site-packages/playwright/sync_api/_generated.py", line 13552, in close
    return mapping.from_maybe_impl(self._sync(self._impl_obj.close(reason=reason)))
                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ubuntu/JellyStream/.venv/lib/python3.12/site-packages/playwright/_impl/_sync_base.py", line 115, in _sync
    return task.result()
           ^^^^^^^^^^^^^
  File "/home/ubuntu/JellyStream/.venv/lib/python3.12/site-packages/playwright/_impl/_browser_context.py", line 616, in close
    await self._channel.send("close", None, {"reason": reason})
  File "/home/ubuntu/JellyStream/.venv/lib/python3.12/site-packages/playwright/_impl/_connection.py", line 69, in send
    return await self._connection.wrap_api_call(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ubuntu/JellyStream/.venv/lib/python3.12/site-packages/playwright/_impl/_connection.py", line 559, in wrap_api_call
    raise rewrite_error(error, f"{parsed_st['apiName']}: {error}") from None
Exception: BrowserContext.close: Connection closed while reading from the driver
root@zero0xypher:/home/ubuntu/JellyStream/api#