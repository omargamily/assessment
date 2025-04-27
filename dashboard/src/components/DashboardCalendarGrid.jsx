import { useState, useEffect } from "react";
import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/react/20/solid";

function classNames(...classes) {
  return classes.filter(Boolean).join(" ");
}

// getDaysInMonth function remains the same as the previous version...
const getDaysInMonth = (year, month, installments) => {
  const firstDayOfMonth = new Date(year, month, 1);
  const lastDayOfMonth = new Date(year, month + 1, 0);
  const daysInMonth = lastDayOfMonth.getDate();

  const firstDayOfWeek = firstDayOfMonth.getDay(); // 0 (Sun) to 6 (Sat)

  const days = [];

  // Days from previous month
  const daysFromPrevMonth = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1; // Adjust for Monday start
  const prevMonth = month === 0 ? 11 : month - 1;
  const prevMonthYear = month === 0 ? year - 1 : year;
  const prevMonthLastDay = new Date(year, month, 0).getDate();

  for (let i = daysFromPrevMonth - 1; i >= 0; i--) {
    const dayNum = prevMonthLastDay - i;
    const dateObj = new Date(prevMonthYear, prevMonth, dayNum);
    days.push({
      date: dateObj.toISOString().split("T")[0], // Keep YYYY-MM-DD format
      isCurrentMonth: false,
    });
  }

  const today = new Date(); // For 'isToday' check only
  const todayDateStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;

  // Days in current month
  for (let i = 1; i <= daysInMonth; i++) {
    // Format the current calendar day as YYYY-MM-DD string for comparison
    const currentYearStr = year;
    const currentMonthStr = String(month + 1).padStart(2, "0"); // month is 0-indexed
    const currentDayStr = String(i).padStart(2, "0");
    const currentDateStr = `${currentYearStr}-${currentMonthStr}-${currentDayStr}`;

    // Check for installment using direct string comparison
    const hasInstallment = installments?.some((installment) => {
      return installment.due_date === currentDateStr;
    });

    days.push({
      date: currentDateStr, // Store the date as YYYY-MM-DD string
      isCurrentMonth: true,
      isToday: currentDateStr === todayDateStr,
      hasInstallment: hasInstallment,
    });
  }

  // Days from next month
  const totalDaysDisplayed = days.length; // Use current length
  const daysToFill = (7 - (totalDaysDisplayed % 7)) % 7; // Calculate remaining days needed for full weeks
  const nextMonth = month === 11 ? 0 : month + 1;
  const nextMonthYear = month === 11 ? year + 1 : year;
  for (let i = 1; i <= daysToFill; i++) {
    const dateObj = new Date(nextMonthYear, nextMonth, i);
    days.push({
      date: dateObj.toISOString().split("T")[0], // Keep YYYY-MM-DD format
      isCurrentMonth: false,
    });
  }

  // Ensure 6 weeks total (42 days) if needed, padding at the end
  while (days.length < 42) {
    const lastDay = days[days.length - 1].date;
    const parts = lastDay.split("-").map(Number);
    const nextDayDate = new Date(parts[0], parts[1] - 1, parts[2]);
    nextDayDate.setDate(nextDayDate.getDate() + 1);
    days.push({
      date: nextDayDate.toISOString().split("T")[0],
      isCurrentMonth: false,
    });
  }

  return days;
};

// Renamed prop: onDateSelect -> onDateStringSelect
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
      onDateStringSelect(null); // Clear selection in parent
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
      onDateStringSelect(null); // Clear selection in parent
    }
  };

  // Modified handler: Passes only the date string to the parent callback
  const handleDayClick = (day) => {
    if (!day.isCurrentMonth) return;

    setSelectedDateStr(day.date);

    // Pass only the selected date string ("YYYY-MM-DD")
    if (onDateStringSelect) {
      onDateStringSelect(day.date);
    }
  };

  return (
    <div className="calendar-grid-container">
      {/* Header (Arrows, Month/Year) remains the same */}
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
      {/* Weekday headers remain the same */}
      <div className="mt-6 grid grid-cols-7 text-xs/6 text-text-secondary text-center">
        <div>M</div>
        <div>T</div>
        <div>W</div>
        <div>T</div>
        <div>F</div>
        <div>S</div>
        <div>S</div>
      </div>
      {/* Grid rendering remains the same */}
      <div className="isolate mt-2 grid grid-cols-7 gap-px bg-border-default text-sm ring-1 ring-border-default">
        {days.map((day, dayIdx) => {
          const isSelected = day.date === selectedDateStr;

          return (
            <button
              key={day.date}
              type="button"
              disabled={!day.isCurrentMonth}
              className={classNames(
                "py-1.5 focus:z-10",
                day.isCurrentMonth
                  ? "bg-background-white"
                  : "bg-background-white",
                !day.isCurrentMonth && "opacity-50",
                dayIdx === 0 && "rounded-tl-lg",
                dayIdx === 6 && "rounded-tr-lg",
                dayIdx === days.length - 7 && "rounded-bl-lg",
                dayIdx === days.length - 1 && "rounded-br-lg"
              )}
              onClick={() => handleDayClick(day)}
            >
              <time
                dateTime={day.date}
                className={classNames(
                  "mx-auto flex size-7 items-center justify-center rounded-full",
                  isSelected && day.isCurrentMonth && "selected-day",
                  day.isToday && "text-red-500",
                  !day.isToday &&
                    !isSelected &&
                    day.isCurrentMonth &&
                    "text-text-primary",
                  day.hasInstallment &&
                    day.isCurrentMonth &&
                    "bg-calendar-highlight-bg ring-1 ring-calendar-highlight-ring",
                  !day.isCurrentMonth && "text-text-secondary"
                )}
              >
                {parseInt(day.date.split("-")[2])}
              </time>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default DashboardCalendarGrid;
