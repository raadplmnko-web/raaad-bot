import time
import requests
import logging
from datetime import datetime
import pytz

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPydldzQZ5a2TQ205plJ3JKA"
CHAT_ID = "687056332"
FINNHUB_KEY = "d6fnilhr01qqnmbpbjc0d6fnilhr01qqnmbpbjcg"
NY_TZ = pytz.timezone("America/New_York")
sent_cache = {}

# قائمة أسهم Penny Stocks الأكثر تداولاً وشهرة
WATCHLIST = [
    "SOUN","PLUG","CLSK","NKLA","IDEX","ILUS","CENN","MULN","FFIE","ZCAR",
    "ATER","BBIG","WKHS","GOEV","XELA","MMAT","TLRY","SNDL","ACB","CGC",
    "CTRM","SHIP","GFAI","MYSZ","DPRO","NAKD","EXPR","AMC","KOSS","BGFV",
    "ABML","ANVS","AREB","ATEK","ATNF","AVCT","AYTU","BFRI","BSFC","BTBT",
    "CABA","CALT","CBAN","CBAT","CDIO","CELZ","CFRX","CLNN","CLRO","CLVS",
    "CNTX","CODX","COEP","COMS","CPSH","CREX","CRIS","CRTX","CRVS","CTXR",
    "DARE","DBVT","DCFC","DFFN","DLPN","DMAC","DNGR","DPSI","DRRX","DTSS",
    "EARS","EBIX","EDSA","ELOX","EMED","ENVB","ENZC","EPIX","EVOK","EVVL",
    "FBIO","FCEL","FFBW","FGEN","FKWL","FLNT","FNCH","FNWB","FPAY","FRZA",
    "GBOX","GCEH","GEVO","GFAI","GIGA","GLBS","GLEO","GLMD","GLSI","GMBL",
    "HALO","HCDI","HCTI","HEPA","HIHO","HLBZ","HLIT","HMBL","HPCO","HPNN",
    "HYMC","HYSR","IKNX","IMAQ","IMCC","IMMP","IMNN","IMPP","IMRX","INDO",
    "INPX","INVU","IONM","ITRM","IXHL","JAGX","JANX","JFIN","JNVR","KAVL",
    "KBNT","KCGI","KERN","KGEI","KPLT","KRRO","KSCP","LBPS","LCFY","LCTX",
    "LGVN","LIQT","LKCO","LMNL","LNTH","LPCN","LPEN","LPSN","LQDA","LRMR",
    "MBRX","MCVT","MDAI","MDJH","MDVX","MEIP","METX","MFON","MGAM","MGTX",
    "MIME","MINM","MKUL","MLEN","MLNK","MLTX","MOFG","MOXC","MPAA","MPVD",
    "MYSZ","NAKD","NBEV","NCPL","NDRA","NEPT","NFYS","NGMS","NHWK","NKGN",
    "NKLA","NLSP","NNAX","NNVC","NOVN","NRSN","NRXP","NSGN","NURO","NVFY",
    "OCGN","OGEN","OLMIX","ONCS","ONVO","OPFI","OPRT","ORGO","ORON","OSST",
    "PAVM","PBAX","PBTS","PCSA","PDEX","PFIE","PGSS","PHGE","PHIO","PHVS",
    "PIXY","PKBO","PLRX","PNTM","POAI","POCI","PRFX","PRLD","PRVB","PRZO",
    "PSTV","PTIX","PULM","PVBC","PVNC","PWFL","QNRX","RCAT","RDHL","RDVT",
    "RLMD","RMBL","RMED","RNER","RNVA","RONI","RPTX","RSLS","RTLX","RVMD",
    "RZLT","SBEV","SBET","SBFM","SBIG","SBOW","SCAP","SCLX","SEEL","SEII",
    "SELB","SFIO","SGBX","SGMO","SHFS","SHIP","SIDU","SIEB","SINT","SKYE",
    "SLNA","SLNO","SMIT","SNAX","SNPX","SOBR","SOPA","SOWG","SPCB","SPGX",
    "SPKL","SPRC","SPRB","SPRO","SPRQ","SPTY","SQFT","SREA","SRTS","SRZN",
    "SSSS","STAF","STCN","STGW","STPC","STPK","STRM","STSS","STXS","SUGP",
    "SUNW","SURF","SVNA","SWAG","SWAV","SWKH","SYRS","SYTA","TALS","TBLT",
    "TCBP","TCON","TCRT","TDAC","TEAT","TFFP","TGLO","THTX","TIRX","TLGA",
    "TLRY","TMDI","TMBR","TMPO","TNXP","TPVG","TRCA","TRNX","TROO","TROV",
    "TRVI","TRXA","TTCF","TTOO","TTSH","TTNP","TTSH","TUNL","TVTX","TXMD",
    "UAVS","UBXG","UCBI","UCON","UFLX","UGRO","ULBI","ULBR","UMAC","UNFI",
    "URGN","USDP","USEG","USEI","USIO","USWS","UTME","UUUU","VALN","VBIV",
    "VCNX","VEON","VERB","VERO","VHAI","VICP","VISL","VITO","VJGG","VLGEA",
    "VNET","VNRX","VNTR","VOGI","VONE","VORB","VPCO","VRAY","VRDN","VRME",
    "VTAK","VTAQ","VTGN","VTSI","VUZI","VVPR","WAFU","WATT","WAVE","WCLD",
    "WEJO","WETG","WFCF","WHLR","WINT","WISA","WKHS","WLTW","WMPN","WNFT",
    "WNNR","WORX","WPRT","WRTC","WTBA","WTRH","WULF","XBIO","XBIT","XCUR",
    "XELA","XELB","XENE","XFOR","XOMA","XPON","XTIA","XTLB","XWEL","YCBD",
    "YELL","YGTY","YKFS","YMTX","YPIX","YTEN","YVRLF","ZCAR","ZEST","ZFOX",
    "ZIVO","ZJYL","ZKIN","ZNTH","ZSAN","ZTHO","ZVRA","ZWRK","ZYXI"
]

def is_market_time():
    now = datetime.now(NY_TZ)
    if now.weekday() >= 5:
        return False
    t = now.hour * 60 + now.minute
    return (4 * 60) <= t < (16 * 60)

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
        logging.info(f"تلجرام: {res.status_code}")
    except Exception as e:
        logging.error(f"خطأ تلجرام: {e}")

def check_signal(symbol):
    url = "https://finnhub.io/api/v1/quote"
    params = {"symbol": symbol, "token": FINNHUB_KEY}
    try:
        res = requests.get(url, params=params, timeout=5)
        d = res.json()
    except:
        return None

    price  = d.get("c", 0)
    open_  = d.get("o", 0)
    high   = d.get("h", 0)
    low    = d.get("l", 0)
    prev   = d.get("pc", 0)
    volume = d.get("v", 0)

    if not price or not prev or prev == 0:
        return None
    if not (0.50 <= price <= 10.00):
        return None
    if price <= open_:
        return None

    roc          = ((price - prev) / prev) * 100
    candle_range = high - low if high > low else 0.001
    bull_pct     = max(0, (price - open_) / candle_range * 100)
    rsi          = max(0, min(100, 50 + roc * 3))
    adx          = min(100, abs(roc) * 5)
    is_high_vol  = volume > 200_000
    is_mega_vol  = volume > 800_000

    is_blast = is_mega_vol and roc > 2.0 and bull_pct > 50 and adx > 20
    is_call  = bull_pct > 55 and rsi > 52 and roc > 1.5 and is_high_vol
    is_early = roc > 1.0 and is_high_vol and bull_pct > 40

    if not (is_blast or is_call or is_early):
        return None

    atr       = candle_range
    target1   = round(price + atr * 1.0, 3)
    target2   = round(price + atr * 2.0, 3)
    target_g  = round(price + atr * 3.5, 3)
    stop_loss = round(low - atr * 0.3, 3)

    label = "💥 انفجار زخم" if is_blast else "🟢 CALL زخم" if is_call else "⚡ بداية زخم"

    return {
        "symbol": symbol, "price": price,
        "roc": round(roc, 2), "volume": volume,
        "bull_pct": round(bull_pct, 1),
        "target1": target1, "target2": target2,
        "target_g": target_g, "stop_loss": stop_loss,
        "label": label,
    }

def scan():
    found = 0
    for i, symbol in enumerate(WATCHLIST):
        last = sent_cache.get(symbol, 0)
        if time.time() - last < 1800:
            continue

        result = check_signal(symbol)
        if result:
            found += 1
            sent_cache[symbol] = time.time()
            msg = (
                f"{result['label']}\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"📌 *السهم:* `{result['symbol']}`\n"
                f"💵 *السعر:* `${result['price']:.3f}`\n"
                f"⚡ *ROC:* `{result['roc']}%`\n"
                f"📊 *زخم الشمعة:* `{result['bull_pct']}%`\n"
                f"📦 *الفوليوم:* `{result['volume']:,}`\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🎯 *هدف 1:* `${result['target1']}`\n"
                f"🎯 *هدف 2:* `${result['target2']}`\n"
                f"🏆 *الهدف الذهبي:* `${result['target_g']}`\n"
                f"🛑 *وقف الخسارة:* `${result['stop_loss']}`\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🚀 *رادار رعد V6*"
            )
            send_msg(msg)
            time.sleep(1)

        if i % 55 == 0 and i > 0:
            time.sleep(61)

    logging.info(f"✅ انتهى الفحص - {found} إشارة")

# ── تشغيل ──
logging.info("🚀 رادار رعد V6 يعمل...")
send_msg(f"🔥 *رادار رعد V6* 🔥\n\nيراقب {len(WATCHLIST)} سهم Penny Stock معروف!")

while True:
    if not is_market_time():
        now = datetime.now(NY_TZ)
        logging.info(f"⏸️ خارج وقت السوق - {now.strftime('%H:%M')} نيويورك")
        time.sleep(300)
        continue

    scan()
    logging.info("⏰ انتظار 3 دقائق...")
    time.sleep(180)
