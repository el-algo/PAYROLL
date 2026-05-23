from dataclasses import dataclass
from typing import Optional

@dataclass
class Collaborator:
    name: str
    salary: float
    salary_hourly: float
    worked_hours: float
    seventh_day: float
    extra_time: float
    hours_worked: float
    bonus: float
    prime_vacation: float
    vacation: float
    vacation_days: float
    loan: float
    Infonavit: float
    Fonacot: float
    loan_discount: float
    weekly_total: float = 0.0

    is_turn_three: bool = False
    hours_deduction: float = 0.0
    unit: str = ""
    week: Optional[str] = None
    pay_date: Optional[str] = None
    days_worked: float = 0.0
    email: str = ""

    def calculate_days_worked(self) -> None:
        seventh_day = self.hours_worked / (5 if self.is_turn_three else 6)
        denom = 48 if self.is_turn_three else 56
        self.days_worked = (seventh_day + self.hours_worked) * 7 / denom

    def calculate_hours_deduction(self) -> None:
        expected_work_days = 6
        expected_worked_hours = 48
        
        if self.is_turn_three:
            expected_work_days = 5
            expected_worked_hours = 40

        if self.vacation_days == 0.0 and self.worked_hours < expected_worked_hours:
            # Cálculo EXTRA por falta
            # Salario base - Total semanal (Sin deducciones)
            self.hours_deduction = self.salary - self.weekly_total
            self.weekly_total = self.salary


    def weekly_total_calc(self) -> float:
        self.weekly_total = (self.hours_worked * self.salary_hourly) + (self.seventh_day * self.salary_hourly)
