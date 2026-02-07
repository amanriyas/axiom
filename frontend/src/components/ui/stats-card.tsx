"use client";

import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: string | number;
  trend?: number;
  trendLabel?: string;
  icon?: React.ReactNode;
  className?: string;
}

export function StatsCard({
  title,
  value,
  trend,
  trendLabel,
  icon,
  className,
}: StatsCardProps) {
  const isPositive = trend !== undefined && trend > 0;
  const isNegative = trend !== undefined && trend < 0;

  return (
    <Card className={cn("", className)}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">{title}</p>
            <p className="text-3xl font-bold">{value}</p>
            {trend !== undefined && (
              <div className="flex items-center gap-1 text-sm">
                {isPositive ? (
                  <TrendingUp className="h-4 w-4 text-[#22c55e]" />
                ) : isNegative ? (
                  <TrendingDown className="h-4 w-4 text-[#ef4444]" />
                ) : null}
                <span
                  className={cn(
                    isPositive && "text-[#22c55e]",
                    isNegative && "text-[#ef4444]",
                    !isPositive && !isNegative && "text-muted-foreground"
                  )}
                >
                  {trend > 0 ? "+" : ""}
                  {trend}
                  {trendLabel || ""}
                </span>
              </div>
            )}
          </div>
          {icon && (
            <div className="rounded-lg bg-primary/10 p-3">{icon}</div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
