import time
class TimeTool:
    @staticmethod
    def Stamp2FullStr(stamp):
        week = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
        timeArray = time.localtime(stamp)
        endTime1 = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        endTime2 = time.strftime("%w", timeArray)
        return f"{endTime1} {week[int(endTime2)]}"

    @staticmethod
    def Stamp2Str(stamp):
        timeArray = time.localtime(stamp)
        endTime1 = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return f"{endTime1}"
        