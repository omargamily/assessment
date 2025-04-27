import { useState, useEffect } from "react";
import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/react/20/solid";

function classNames(...classes) {
  return classes.filter(Boolean).join(" ");
}

const getDaysInMonth = (year, month, installments) => {
  const firstDayOfMonth = new Date(Date.UTC(year, month, 1));
  const lastDayOfMonth = new Date(Date.UTC(year, month + 1, 0));
  const daysInMonth = lastDayOfMonth.getUTCDate();

  const firstDayOfWeek = firstDayOfMonth.getUTCDay();

  const days = [];

  const daysFromPrevMonth = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1;
  const prevMonthLastDay = new Date(Date.UTC(year, month, 0)).getUTCDate();
  const prevMonth = month === 0 ? 11 : month - 1;
  const prevMonthYear = month === 0 ? year - 1 : year;

  for (let i = daysFromPrevMonth - 1; i >= 0; i--) {
    const dayNum = prevMonthLastDay - i;
    const dateObj = new Date(Date.UTC(prevMonthYear, prevMonth, dayNum));
    days.push({
      date: dateObj.toISOString().split("T")[0],
      isCurrentMonth: false,
      hasInstallment: false,
      isPaid: false,
    });
  }

  const today = new Date();
  const todayDateStr = `${today.getFullYear()}-${String(
    today.getMonth() + 1
  ).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;

  for (let i = 1; i <= daysInMonth; i++) {
    const currentYearStr = year;
    const currentMonthStr = String(month + 1).padStart(2, "0");
    const currentDayStr = String(i).padStart(2, "0");
    const currentDateStr = `${currentYearStr}-${currentMonthStr}-${currentDayStr}`;

    const todaysInstallments =
      installments?.filter((inst) => inst.due_date === currentDateStr) || [];
    const hasInstallment = todaysInstallments.length > 0;
    // Make status check case-insensitive
    const isPaid =
      hasInstallment &&
      todaysInstallments.some((inst) => inst.status?.toLowerCase() === "paid");

    days.push({
      date: currentDateStr,
      isCurrentMonth: true,
      isToday: currentDateStr === todayDateStr,
      hasInstallment: hasInstallment,
      isPaid: isPaid,
    });
  }

  while (days.length < 42) {
    if (days.length === 0) {
      console.error(
        "Calendar generation error: Empty days array before final padding."
      );
      break;
    }
    const lastDayEntry = days[days.length - 1];
    if (!lastDayEntry || typeof lastDayEntry.date !== "string") {
      console.error(
        "Calendar generation error: Invalid last day entry before padding.",
        lastDayEntry
      );
      break;
    }
    const lastDateStr = lastDayEntry.date;
    const parts = lastDateStr.split("-").map(Number);

    const nextDayDate = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2]));
    nextDayDate.setUTCDate(nextDayDate.getUTCDate() + 1);

    days.push({
      date: nextDayDate.toISOString().split("T")[0],
      isCurrentMonth: false,
      hasInstallment: false,
      isPaid: false,
    });
  }

  return days.slice(0, 42);
};

const DashboardCalendarGrid = ({ installments, onDateStringSelect }) => {
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth());
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear());
  const [days, setDays] = useState([]);
  const [selectedDateStr, setSelectedDateStr] = useState(null);

  useEffect(() => {
    setDays(getDaysInMonth(currentYear, currentMonth, installments));
  }, [currentYear, currentMonth, installments]);

  const handlePreviousMonth = () => {
    if (currentMonth === 0) {
      setCurrentMonth(11);
      setCurrentYear(currentYear - 1);
    } else {
      setCurrentMonth(currentMonth - 1);
    }
    setSelectedDateStr(null);
    if (onDateStringSelect) {
      onDateStringSelect(null);
    }
  };

  const handleNextMonth = () => {
    if (currentMonth === 11) {
      setCurrentMonth(0);
      setCurrentYear(currentYear + 1);
    } else {
      setCurrentMonth(currentMonth + 1);
    }
    setSelectedDateStr(null);
    if (onDateStringSelect) {
      onDateStringSelect(null);
    }
  };

  const handleDayClick = (day) => {
    if (!day.isCurrentMonth) return;

    setSelectedDateStr(day.date);

    if (onDateStringSelect) {
      onDateStringSelect(day.date);
    }
  };

  return (
    <div className="calendar-grid-container">
      <div className="flex items-center text-text-primary p-2">
        <button
          type="button"
          className="-m-1.5 flex flex-none items-center justify-center p-1.5 text-text-secondary"
          onClick={handlePreviousMonth}
        >
          <span className="sr-only">Previous month</span>
          <ChevronLeftIcon className="size-5" aria-hidden="true" />
        </button>
        <div className="flex-auto text-sm font-semibold text-center">
          {new Date(currentYear, currentMonth).toLocaleString("default", {
            month: "long",
            year: "numeric",
          })}
        </div>
        <button
          type="button"
          className="-m-1.5 flex flex-none items-center justify-center p-1.5 text-text-secondary"
          onClick={handleNextMonth}
        >
          <span className="sr-only">Next month</span>
          <ChevronRightIcon className="size-5" aria-hidden="true" />
        </button>
      </div>
      <div className="mt-6 grid grid-cols-7 text-xs/6 text-text-secondary text-center">
        <div>M</div>
        <div>T</div>
        <div>W</div>
        <div>T</div>
        <div>F</div>
        <div>S</div>
        <div>S</div>
      </div>
      <div className="isolate mt-2 grid grid-cols-7 gap-px bg-border-default text-sm ring-1 ring-border-default">
        {days.map((day, dayIdx) => {
          const key = day.date ? `${day.date}-${dayIdx}` : dayIdx;
          const isSelected = day.date === selectedDateStr;

          return (
            <button
              key={key}
              type="button"
              disabled={!day.isCurrentMonth}
              className={classNames(
                "py-1.5 focus:z-10",
                day && day.isCurrentMonth
                  ? "bg-background-white"
                  : "bg-background-white",
                day && !day.isCurrentMonth && "opacity-50",
                dayIdx === 0 && "rounded-tl-lg",
                dayIdx === 6 && "rounded-tr-lg",
                dayIdx === days.length - 7 && "rounded-bl-lg",
                dayIdx === days.length - 1 && "rounded-br-lg"
              )}
              onClick={() => handleDayClick(day)}
            >
              {day && day.date && (
                <time
                  dateTime={day.date}
                  className={classNames(
                    "mx-auto flex size-7 items-center justify-center rounded-full",
                    isSelected && day.isCurrentMonth && "selected-day",
                    day.isToday && "text-red-500 font-bold",
                    !day.isToday &&
                      !isSelected &&
                      day.isCurrentMonth &&
                      "text-text-primary",
                    day.isPaid &&
                      day.isCurrentMonth &&
                      "bg-green-300 ring-1 ring-green-400",
                    day.hasInstallment &&
                      !day.isPaid &&
                      day.isCurrentMonth &&
                      "bg-calendar-highlight-bg ring-1 ring-calendar-highlight-ring",
                    !day.isCurrentMonth && "text-text-secondary"
                  )}
                >
                  {typeof day.date === "string"
                    ? parseInt(day.date.split("-")[2])
                    : "?"}
                </time>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default DashboardCalendarGrid;
