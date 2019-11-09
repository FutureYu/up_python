import time
class TimeTool:
    @staticmethod
    def Stamp2FullStr(stamp):
        startstamp = 1567353600
        weekNum = (stamp - startstamp) // 604800 + 1
        week = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
        timeArray = time.localtime(stamp)
        endTime1 = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        endTime2 = time.strftime("%w", timeArray)
        return f"{endTime1} 第{weekNum}周 {week[int(endTime2)]}"

    @staticmethod
    def Stamp2Str(stamp):
        timeArray = time.localtime(stamp)
        endTime1 = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return f"{endTime1}"
        