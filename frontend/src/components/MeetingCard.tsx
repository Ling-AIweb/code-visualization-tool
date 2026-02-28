import { useState } from 'react'
import { Users, Clock, MapPin, Video, Copy, Check, Plus, ChevronRight, Calendar, Bell } from 'lucide-react'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

interface MeetingCardProps {
  className?: string
}

export default function MeetingCard({ className = '' }: MeetingCardProps) {
  const [copied, setCopied] = useState(false)
  const [showAllParticipants, setShowAllParticipants] = useState(false)

  const meetingData = {
    date: '7月9日（周二）17:00-18:00（GMT+8）',
    title: '钉钉日历验收流程宣讲',
    calendarType: '我的日历',
    belongsTo: '归属于钉钉',
    location: 'D1-16-115 多媒体会议室',
    meetingNumber: '123 121 224',
    organizer: {
      name: '王强',
      avatar: 'https://img.alicdn.com/imgextra/i4/6000000004961/O1CN01rsoRTP1mWC0VECf9j_!!6000000004961-2-gg_dtc.png',
      status: 'accepted' as const,
      isOrganizer: true
    },
    participants: [
      {
        id: '1',
        name: '刘玉',
        avatar: 'https://img.alicdn.com/imgextra/i4/6000000002124/O1CN01kR2AxS1RYqMuPZDub_!!6000000002124-2-gg_dtc.png',
        status: 'accepted' as const
      },
      {
        id: '2',
        name: '李倩',
        avatar: 'https://img.alicdn.com/imgextra/i1/6000000001410/O1CN01VL0Siy1MHpZrzr1mw_!!6000000001410-2-gg_dtc.png',
        status: 'pending' as const
      },
      {
        id: '3',
        name: '马冬梅',
        avatar: 'https://img.alicdn.com/imgextra/i4/6000000002124/O1CN01kR2AxS1RYqMuPZDub_!!6000000002124-2-gg_dtc.png',
        status: 'accepted' as const
      },
      {
        id: '4',
        name: '马冬梅',
        avatar: 'https://img.alicdn.com/imgextra/i4/6000000002124/O1CN01kR2AxS1RYqMuPZDub_!!6000000002124-2-gg_dtc.png',
        status: 'accepted' as const
      },
      {
        id: '5',
        name: '马冬梅',
        avatar: 'https://img.alicdn.com/imgextra/i4/6000000002124/O1CN01kR2AxS1RYqMuPZDub_!!6000000002124-2-gg_dtc.png',
        status: 'accepted' as const
      }
    ],
    preMeetingSummary: '会前主要提示会议准备事项，如是否开启听记、参会人状态、地理位置建议，会中支持外部人员查看实时发言内容与结论内容与结论内容与结论进展，当前属未覆盖',
    agenda: [
      '讨论开启听记、参会人状态、地理位议。',
      '讨论下周进展',
      '会议总结'
    ],
    settings: {
      createGroup: true,
      busy: false,
      calendarColor: '#0066FF',
      reminder: '开始前15分钟，应用弹窗提醒我'
    }
  }

  const handleCopyMeetingNumber = () => {
    navigator.clipboard.writeText(meetingData.meetingNumber)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const displayedParticipants = showAllParticipants 
    ? meetingData.participants 
    : meetingData.participants.slice(0, 4)

  const participantStatusColor = (status: string) => {
    switch (status) {
      case 'accepted':
        return 'shadow-[inset_0_0_0_1px_#00BB55]'
      case 'pending':
        return 'shadow-[inset_0_0_0_1px_#FD9100]'
      case 'declined':
        return 'shadow-[inset_0_0_0_1px_#FF4D4F]'
      default:
        return ''
    }
  }

  return (
    <div className={twMerge(clsx('flex justify-center items-center min-h-screen bg-gray-50 p-4', className))}>
      <div 
        className="w-[702px] h-[520px] bg-white rounded-[24px] shadow-[0px_4px_20px_-1px_rgba(0,0,0,0.16)] overflow-hidden flex flex-col"
        style={{
          background: 'linear-gradient(#0066FF0A, #0066FF0A), linear-gradient(#FFFFFF, #FFFFFF)'
        }}
      >
        {/* 顶部时间栏 */}
        <div className="flex items-center justify-between px-4 py-3 h-[24px]">
          <div className="flex items-center bg-blue-50/50 rounded-full px-2 py-0.5">
            <div className="w-1.5 h-1.5 bg-blue-500 rounded-full" />
            <span className="text-sm text-blue-500 ml-2">{meetingData.date}</span>
          </div>
          <img 
            src="https://img.alicdn.com/imgextra/i2/6000000000056/O1CN01uzx4g21CHhIrLH6uJ_!!6000000000056-2-gg_dtc.png" 
            alt="" 
            className="w-[52px] h-[24px]"
          />
        </div>

        {/* 主体内容 */}
        <div className="flex flex-1 mt-2">
          {/* 左侧会议信息 */}
          <div className="w-[360px] bg-white rounded-l-[24px] p-4 flex flex-col">
            {/* 会议标题 */}
            <div className="mb-5">
              <h1 className="text-xl font-medium text-[#171A1D] mb-1">
                {meetingData.title}
              </h1>
              <div className="flex items-center gap-3 text-xs text-[#181C1F66]">
                <span>{meetingData.calendarType}</span>
                <div className="w-[2px] h-2 bg-[#181C1F66]" />
                <span>{meetingData.belongsTo}</span>
              </div>
            </div>

            {/* 地点 */}
            <div className="bg-[#FAFAFA] rounded-lg p-2.5 flex items-center gap-2 mb-2">
              <MapPin className="w-6 h-6 flex-shrink-0" />
              <span className="text-sm text-[#181C1F]">{meetingData.location}</span>
            </div>

            {/* 视频会议 */}
            <div className="bg-[#FAFAFA] rounded-lg p-2.5 flex items-center gap-2 mb-5">
              <Video className="w-6 h-6 flex-shrink-0" />
              <span className="text-sm text-[#181C1F]">钉钉视频会议</span>
              <div className="w-[2px] h-2 bg-[#181C1F66] ml-1" />
              <span className="text-sm text-[#181C1F99]">会议号：{meetingData.meetingNumber}</span>
              <button 
                onClick={handleCopyMeetingNumber}
                className="ml-auto hover:bg-gray-200 rounded p-0.5 transition-colors"
              >
                {copied ? (
                  <Check className="w-3 h-3 text-green-500" />
                ) : (
                  <Copy className="w-3 h-3 text-gray-400" />
                )}
              </button>
            </div>

            {/* 参会人员 */}
            <div className="flex-1 overflow-hidden">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  <span className="text-sm text-[#181C1F]">
                    {meetingData.organizer.name} 邀请16人，7人接受
                  </span>
                </div>
                <button className="flex items-center gap-1 text-xs text-[#181C1F66] hover:text-[#181C1F] transition-colors">
                  <span>添加成员</span>
                  <Plus className="w-3 h-3" />
                </button>
              </div>

              {/* 组织者 */}
              <div className="relative w-[106px] h-[26px] mb-2">
                <div className="absolute left-3 top-0 w-[94px] h-[24px] bg-[#F2F2F6] rounded-r-full" />
                <div className={`absolute left-0 top-0 w-6 h-6 rounded-full bg-white ${participantStatusColor(meetingData.organizer.status)} z-10`}>
                  <img src={meetingData.organizer.avatar} alt={meetingData.organizer.name} className="w-5 h-5 rounded-full m-0.5" />
                </div>
                <div className="absolute left-4 bottom-0 w-2.5 h-2.5 bg-green-500 rounded-full z-20" />
                <span className="absolute left-7 top-0.5 text-xs text-[#181C1F] whitespace-nowrap z-30">
                  {meetingData.organizer.name} (组织人)
                </span>
              </div>

              {/* 参会人员列表 */}
              <div className="flex flex-wrap gap-2">
                {displayedParticipants.map((participant) => (
                  <div key={participant.id} className="relative w-[58px] h-[26px]">
                    <div className="absolute left-3 top-0 w-[46px] h-[24px] bg-[#F2F2F6] rounded-r-full" />
                    <div className={`absolute left-0 top-0 w-6 h-6 rounded-full bg-white ${participantStatusColor(participant.status)} z-10`}>
                      <img src={participant.avatar} alt={participant.name} className="w-5 h-5 rounded-full m-0.5" />
                    </div>
                    <div className="absolute left-4 bottom-0 w-2.5 h-2.5 bg-green-500 rounded-full z-20" />
                    <span className="absolute right-1.5 top-0.5 text-xs text-[#181C1F] whitespace-nowrap z-30">
                      {participant.name}
                    </span>
                  </div>
                ))}
                
                {!showAllParticipants && meetingData.participants.length > 4 && (
                  <button 
                    onClick={() => setShowAllParticipants(true)}
                    className="w-[60px] h-[24px] bg-[#F2F2F6] rounded-lg flex items-center justify-center text-xs text-[#181C1F66] hover:bg-gray-200 transition-colors"
                  >
                    展开全部
                  </button>
                )}
              </div>
            </div>

            {/* 会议设置选项 */}
            <div className="mt-5 space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Users className="w-4 h-4" />
                  <span className="text-sm text-[#181C1F]">创建会议群</span>
                </div>
                <ChevronRight className="w-4 h-4 text-gray-400" />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Clock className="w-4 h-4" />
                  <span className="text-sm text-[#181C1F]">忙碌</span>
                </div>
                <Plus className="w-3 h-3 text-gray-400" />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div 
                    className="w-3 h-3 rounded bg-blue-500" 
                    style={{ backgroundColor: meetingData.settings.calendarColor }}
                  />
                  <span className="text-sm text-[#181C1F]">日历颜色</span>
                </div>
                <Plus className="w-3 h-3 text-gray-400" />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Bell className="w-4 h-4" />
                  <span className="text-sm text-[#181C1F]">{meetingData.settings.reminder}</span>
                </div>
                <ChevronRight className="w-4 h-4 text-gray-400" />
              </div>
            </div>
          </div>

          {/* 右侧会前摘要 */}
          <div className="w-[330px] relative ml-1">
            <img 
              src="https://img.alicdn.com/imgextra/i1/6000000005853/O1CN01fBkxar1t6jIQiv7m1_!!6000000005853-2-gg_dtc.png" 
              alt="" 
              className="w-full h-full rounded-r-[24px]"
            />
            <div className="absolute inset-0 rounded-r-[24px] p-4 flex flex-col">
              {/* 会前摘要 */}
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-2">
                  <Calendar className="w-5 h-5" />
                  <span className="text-sm font-medium text-[#050505]">会前摘要</span>
                </div>
                <p className="text-sm text-[#181C1F99] leading-6 whitespace-pre-wrap overflow-hidden line-clamp-4">
                  {meetingData.preMeetingSummary}
                </p>
              </div>

              {/* 会议议程 */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm font-medium text-[#050505]">会议议程</span>
                </div>
                <ol className="text-sm text-[#181C1F99] leading-6 list-decimal list-inside space-y-1">
                  {meetingData.agenda.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ol>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
