root@zero0xypher:/home/ubuntu# ls -la /media/jellyfin/serienstream | head
find /media/jellyfin/serienstream -name '.structure_progress.json' -o -name '*.strm' | head -n 20
python3 - <<'PY'
import json
from pathlib import Path

p = Path("/home/ubuntu/JellyStream/sites/serienstream/data/final_series_data.json")
data = json.loads(p.read_text(encoding="utf-8"))

series_with_streams = 0
episodes_with_streams = 0
for s in data.get("series", []):
    has_stream = False
    for season in s.get("seasons", {}).values():
        for ep in season.get("episodes", {}).values():
            if ep.get("total_streams", 0) > 0:
                episodes_with_streams += 1
                has_stream = True
    if has_stream:
        series_with_streams += 1

print("series_with_streams:", series_with_streams)
print("episodes_with_streams:", episodes_with_streams)
PY
total 42964
drwxr-xr-x     3 root root   4096 Mar 20 17:26 #COMPASS2.0 ANIMATION PROJECT
drwxr-xr-x     4 root root   4096 Mar 20 17:26 #LikeMe
drwxr-xr-x     4 root root   4096 Mar 20 17:26 #TextMeWhenYouGetHome
drwxr-xr-x     3 root root   4096 Mar 20 17:26 #blackAF
drwxr-xr-x     3 root root   4096 Mar 20 17:26 #unterAlmans – Migrantische Geschichte(n)
drwxr-xr-x     3 root root   4096 Mar 20 17:26 (Un)Well
drwxr-xr-x 10554 root root 466944 Mar 20 17:38 .
drwxr-xr-x     3 root root   4096 Mar 20 17:26 ..
-rw-r--r--     1 root root 298534 Mar 20 17:27 .structure_progress.json
/media/jellyfin/serienstream/.structure_progress.json
/media/jellyfin/serienstream/(Un)Well/Season 01/S01E02.strm
/media/jellyfin/serienstream/(Un)Well/Season 01/S01E01.strm
/media/jellyfin/serienstream/(Un)Well/Season 01/S01E04.strm
/media/jellyfin/serienstream/(Un)Well/Season 01/S01E03.strm
/media/jellyfin/serienstream/(Un)Well/Season 01/S01E06.strm
/media/jellyfin/serienstream/(Un)Well/Season 01/S01E05.strm
/media/jellyfin/serienstream/#TextMeWhenYouGetHome/Season 02/S02E11.strm
/media/jellyfin/serienstream/#TextMeWhenYouGetHome/Season 02/S02E06.strm
/media/jellyfin/serienstream/#TextMeWhenYouGetHome/Season 02/S02E02.strm
/media/jellyfin/serienstream/#TextMeWhenYouGetHome/Season 02/S02E05.strm
/media/jellyfin/serienstream/#TextMeWhenYouGetHome/Season 02/S02E10.strm
/media/jellyfin/serienstream/#TextMeWhenYouGetHome/Season 02/S02E12.strm
/media/jellyfin/serienstream/#TextMeWhenYouGetHome/Season 02/S02E01.strm
/media/jellyfin/serienstream/#TextMeWhenYouGetHome/Season 02/S02E07.strm
/media/jellyfin/serienstream/#TextMeWhenYouGetHome/Season 02/S02E04.strm
/media/jellyfin/serienstream/#TextMeWhenYouGetHome/Season 02/S02E13.strm
/media/jellyfin/serienstream/#TextMeWhenYouGetHome/Season 02/S02E09.strm
/media/jellyfin/serienstream/#TextMeWhenYouGetHome/Season 02/S02E03.strm
/media/jellyfin/serienstream/#TextMeWhenYouGetHome/Season 02/S02E08.strm
series_with_streams: 3089
episodes_with_streams: 73671



root@zero0xypher:/home/ubuntu/JellyStream/sites/serienstream# cd /home/ubuntu/JellyStream/sites/serienstream
python3 7_jellyfin_structurer.py --clear-progress --api-url http://localhost:3000/stream/redirect
🗑️  Progress cleared
🚀 Starting Jellyfin structure generation...
🌍 Language Priority: Englisch
2026-03-20 18:07:48,876 - INFO - Loaded 10552 series from /home/ubuntu/JellyStream/sites/serienstream/data/final_series_data.json
📊 Total series: 10,552
✅ Already processed: 0
⏳ Remaining: 10,552
💾 Disk usage: 26.2% (50GB / 192GB)
📺 [1/10552] und dann noch Paula
📺 [2/10552] hackLegend of the Twilight
📺 [3/10552] hackRoots
📺 [4/10552] hackSign
📺 [5/10552] (Un)Well
📺 [6/10552] #blackAF
📺 [7/10552] #COMPASS2.0 ANIMATION PROJECT
📺 [8/10552] #LikeMe
📺 [9/10552] #TextMeWhenYouGetHome
📺 [10/10552] #unterAlmans – Migrantische Geschichte(n)
📺 [100/10552] 666 Park Avenue
📺 [200/10552] Acapulco H.E.A.T
📺 [300/10552] Akebi-chan no Sailor Fuku
📺 [400/10552] Alles Betty!
📺 [500/10552] American Soul
📺 [600/10552] Anthracite
📺 [700/10552] Asphalt-Cowboys – Ladies on Tour
📺 [800/10552] B't X
📺 [900/10552] Bargain
📺 [1000/10552] Bella and the Bulldogs
✅ Batch 1000: 8055 episodes, 0 movies created
📊 Total progress: 1000/10552 (9.5%)
📺 [1100/10552] Bing
📺 [1200/10552] Blood Ties - Biss aufs Blut
📺 [1300/10552] Bordertown (US)
📺 [1400/10552] Bulge Bracket
📺 [1500/10552] Carl Hiaasen’s Bad Monkey
📺 [1600/10552] Chicago Party Aunt
📺 [1700/10552] Close to Me
📺 [1800/10552] Courage der feige Hund
📺 [1900/10552] Dallas
📺 [2000/10552] Das Horn
✅ Batch 2000: 16233 episodes, 0 movies created
📊 Total progress: 2000/10552 (19.0%)
📺 [2100/10552] Dead Mount Death Play
📺 [2200/10552] Der Bestatter
📺 [2300/10552] Der Kroatien Krimi
📺 [2400/10552] Descendants of the Sun
📺 [2500/10552] Die Biber Brüder
📺 [2600/10552] Die grünen Handschuhe
📺 [2700/10552] Die neue Zeit
📺 [2800/10552] Die Supermonster
📺 [2900/10552] Diplomatische Beziehungen
📺 [3000/10552] Dora
✅ Batch 3000: 20435 episodes, 0 movies created
📊 Total progress: 3000/10552 (28.4%)
📺 [3100/10552] Dummy
📺 [3200/10552] Ein Schritt zum Abgrund
📺 [3300/10552] Enemy of the People
📺 [3400/10552] Extreme Dinosaurs
📺 [3500/10552] FC Barcelona – Eine neue Ära
📺 [3600/10552] Forecasting Love and Weather
📺 [3700/10552] Funeral for a Dog
📺 [3800/10552] Geheimnisse des BND
📺 [3900/10552] Girls
📺 [4000/10552] Grand Blue
✅ Batch 4000: 27516 episodes, 0 movies created
📊 Total progress: 4000/10552 (37.9%)
📺 [4100/10552] Hacking the System
📺 [4200/10552] Hart of Dixie
📺 [4300/10552] Hell on Wheels
📺 [4400/10552] Hinomaru Zumou
📺 [4500/10552] House of David
📺 [4600/10552] Ice Road Rescue – Extremrettung in Norwegen
📺 [4700/10552] Indiens in Verruf geratene Milliardäre
📺 [4800/10552] Isekai Nonbiri Nouka
📺 [4900/10552] Jetzt erst recht!
📺 [5000/10552] Kaitou Joker
✅ Batch 5000: 33673 episodes, 0 movies created
📊 Total progress: 5000/10552 (47.4%)
📺 [5100/10552] Kein Fall für F.B.I
📺 [5200/10552] Kinnikuman Perfect Origin Hen
📺 [5300/10552] Kono Healer, Mendokusai
📺 [5400/10552] La storia della Arcana Famiglia
📺 [5500/10552] Leopard Skin
📺 [5600/10552] Lolek und Bolek
📺 [5700/10552] Lucky Luke (Realserie)
📺 [5800/10552] Maji de Watashi ni Koi Shinasai!
📺 [5900/10552] Marshals A Yellowstone Story
📺 [6000/10552] Medalist
✅ Batch 6000: 39885 episodes, 0 movies created
📊 Total progress: 6000/10552 (56.9%)
📺 [6100/10552] Midnight, Texas
📺 [6200/10552] MobLand
📺 [6300/10552] Mother of the Goddess’ Dormitory
📺 [6400/10552] My Friend's Little Sister Has It In for Me!
📺 [6500/10552] Neds ultimativer Schulwahnsinn
📺 [6600/10552] No Escape
📺 [6700/10552] Oddballs (2022)
📺 [6800/10552] Orient
📺 [6900/10552] Paradise City
📺 [7000/10552] Piets irre Pleiten
✅ Batch 7000: 47061 episodes, 0 movies created
📊 Total progress: 7000/10552 (66.3%)
📺 [7100/10552] Power Rangers Space Patrol Delta
📺 [7200/10552] Q-Force
📺 [7300/10552] Real Humans – Echte Menschen
📺 [7400/10552] revisions
📺 [7500/10552] Ronja Räubertochter
📺 [7600/10552] Sally Bollywood
📺 [7700/10552] Schooled
📺 [7800/10552] Senjou no Valkyria Valkyria Chronicles
📺 [7900/10552] Shigurui
📺 [8000/10552] Sintonia
✅ Batch 8000: 54102 episodes, 0 movies created
📊 Total progress: 8000/10552 (75.8%)
📺 [8100/10552] Solsidan
📺 [8200/10552] Spooks Code 9
📺 [8300/10552] Station Eleven
📺 [8400/10552] Summer Camp Island
📺 [8500/10552] Tacoma FD
📺 [8600/10552] Tengoku Daimakyou
📺 [8700/10552] The Bisexual
📺 [8800/10552] The Detective Is Already Dead
📺 [8900/10552] The Gold
📺 [9000/10552] The Last Man on Earth
✅ Batch 9000: 63020 episodes, 0 movies created
📊 Total progress: 9000/10552 (85.3%)
📺 [9100/10552] The Nineties
📺 [9200/10552] The Runarounds
📺 [9300/10552] The Vince Staples Show
📺 [9400/10552] Tilo Neumann und das Universum
📺 [9500/10552] Top Gear USA
📺 [9600/10552] Trolls - Die Party geht weiter!
📺 [9700/10552] UFOs – Zwischen Wahrheit und Verschwörung
📺 [9800/10552] Unspeakable
📺 [9900/10552] VerdachtMord
📺 [10000/10552] Wage es nicht
✅ Batch 10000: 70982 episodes, 0 movies created
📊 Total progress: 10000/10552 (94.8%)
📺 [10100/10552] Welcome to the Family
📺 [10200/10552] Wilde Dynastien - Die Clans der Tiere
📺 [10300/10552] Women Who Rock
📺 [10400/10552] Yoru no Kurage wa Oyogenai
📺 [10500/10552] ZERV – Zeit der Abrechnung

============================================================
📊 JELLYFIN STRUCTURE GENERATION COMPLETE
============================================================
🌍 Language Priority: Englisch
✅ Series processed: 10,552
✅ Series created: 10,552
✅ Seasons created: 6,504
✅ Episodes created: 73,671
🎬 Movies created: 0

📺 Episodes by language:
   Englisch: 73,671
🎬 Movies by language:

⏭️  Episodes skipped (no streams): 223,112
⏭️  Episodes skipped (no supported language): 0
⏭️  Movies skipped (no streams): 0
⏭️  Movies skipped (no supported language): 0
❌ Errors: 0
📁 Output: /media/jellyfin/serienstream
============================================================
🎯 Ready for Jellyfin!
   1. Scan library in Jellyfin
   2. Disable image downloads (recommended)
   3. Movies are in Season 00
root@zero0xypher:/home/ubuntu/JellyStream/sites/serienstream#

root@zero0xypher:/home/ubuntu/JellyStream/sites/serienstream# find /media/jellyfin/serienstream -name '*.strm' | head
/media/jellyfin/serienstream/(Un)Well/Season 01/S01E02.strm
/media/jellyfin/serienstream/(Un)Well/Season 01/S01E01.strm
/media/jellyfin/serienstream/(Un)Well/Season 01/S01E04.strm
/media/jellyfin/serienstream/(Un)Well/Season 01/S01E03.strm
/media/jellyfin/serienstream/(Un)Well/Season 01/S01E06.strm
/media/jellyfin/serienstream/(Un)Well/Season 01/S01E05.strm
/media/jellyfin/serienstream/#TextMeWhenYouGetHome/Season 02/S02E11.strm
/media/jellyfin/serienstream/#TextMeWhenYouGetHome/Season 02/S02E06.strm
/media/jellyfin/serienstream/#TextMeWhenYouGetHome/Season 02/S02E02.strm
/media/jellyfin/serienstream/#TextMeWhenYouGetHome/Season 02/S02E05.strm
root@zero0xypher:/home/ubuntu/JellyStream/sites/serienstream#
