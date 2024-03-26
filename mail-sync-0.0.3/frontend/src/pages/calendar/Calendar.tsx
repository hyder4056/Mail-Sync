/* eslint-disable @typescript-eslint/no-unused-vars */
// import { useEffect, useState } from 'react';

import { Calendar, type CalendarProps, Typography, Avatar, Flex } from 'antd';
import type { Dayjs } from 'dayjs';
import dayjs from 'dayjs';

import type { IEvent } from '../../common/types';

export default function CalendarView({
  setSelectedDay,
  events,
  userLinkedMail,
}: {
  setSelectedDay: (value: Dayjs) => void;
  events: Record<string, IEvent[]>;
  userLinkedMail: Record<string, string>;
}) {
  const cellRender: CalendarProps<Dayjs>['cellRender'] = (current) => {
    const listData = events[current.format('MMDD')] || [];

    return (
      <>
        {listData.map((item) => (
          <>
            <Flex align="center" key={item.id}>
              <div>
                <Avatar size={20} src={userLinkedMail[item.userEmail]} />
              </div>
              <Typography.Text
                type="secondary"
                style={{ fontSize: '0.8rem', paddingLeft: '0.5rem', wordBreak: 'normal' }}
              >
                {dayjs(item.start).format('HH:mm')}
              </Typography.Text>
              <Typography.Text ellipsis style={{ fontSize: '0.9rem', paddingLeft: '0.5rem', wordBreak: 'normal' }}>
                {item.title}
              </Typography.Text>
            </Flex>
          </>
        ))}
      </>
    );
  };

  const onPanelChange: CalendarProps<Dayjs>['onPanelChange'] = (value) => {
    setSelectedDay(value);
  };
  return (
    <Calendar
      mode="month"
      onPanelChange={onPanelChange}
      cellRender={cellRender}
      onSelect={(day, info) => {
        if (info.source === 'date') {
          setSelectedDay(day);
        }
      }}
    />
  );
}
