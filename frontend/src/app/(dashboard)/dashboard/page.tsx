"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Clock,
  RefreshCw,
  CheckCircle,
  Timer,
  Plus,
  Upload,
  Eye,
  ArrowRight,
  ShieldAlert,
  AlertTriangle,
  XCircle,
  CheckSquare,
} from "lucide-react";
import { TopNav } from "@/components/layout/top-nav";
import { StatsCard } from "@/components/ui/stats-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { employeeApi, complianceApi, approvalApi } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { Employee, ComplianceItem, ComplianceSummary } from "@/types";

function formatTimeAgo(date: string): string {
  const now = new Date();
  const past = new Date(date);
  const diffMs = now.getTime() - past.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
}

export default function DashboardPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [complianceAlerts, setComplianceAlerts] = useState<ComplianceItem[]>([]);
  const [pendingApprovals, setPendingApprovals] = useState(0);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const { user } = useAuth();

  useEffect(() => {
    if (!user) return; // Wait for auth to be confirmed
    const fetchData = async () => {
      try {
        const [empData, alertsData, approvalCount] = await Promise.all([
          employeeApi.list(),
          complianceApi.getAlerts().catch(() => []),
          approvalApi.getPendingCount().catch(() => ({ count: 0 })),
        ]);
        setEmployees(empData);
        setComplianceAlerts(alertsData);
        setPendingApprovals(approvalCount.count);
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user]);

  // Calculate stats
  const completedEmployees = employees.filter((e) => e.status === "completed");
  const avgTimeDays = completedEmployees.length > 0
    ? completedEmployees.reduce((sum, e) => {
        const start = new Date(e.created_at).getTime();
        const end = new Date(e.updated_at).getTime();
        return sum + (end - start) / (1000 * 60 * 60 * 24);
      }, 0) / completedEmployees.length
    : 0;

  const stats = {
    pending: employees.filter((e) => e.status === "pending").length,
    inProgress: employees.filter((e) => e.status === "onboarding").length,
    completed: completedEmployees.length,
    avgTime: Math.round(avgTimeDays * 10) / 10,
  };

  const recentEmployees = employees.slice(0, 5);

  const getStepLabel = (status: string) => {
    switch (status) {
      case "pending":
        return "Not started";
      case "onboarding":
        return "In progress...";
      case "completed":
        return "All complete";
      case "failed":
        return "Failed";
      default:
        return status;
    }
  };

  return (
    <div className="flex flex-col">
      <TopNav title="Dashboard" />

      <div className="flex-1 space-y-6 p-6">
        {/* Stats Cards */}
        {loading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatsCard
              title="Pending Onboardings"
              value={stats.pending}
              icon={<Clock className="h-5 w-5 text-primary" />}
            />
            <StatsCard
              title="In Progress"
              value={stats.inProgress}
              icon={<RefreshCw className="h-5 w-5 text-primary" />}
            />
            <StatsCard
              title="Completed This Month"
              value={stats.completed}
              icon={<CheckCircle className="h-5 w-5 text-primary" />}
            />
            <StatsCard
              title="Avg. Time to Complete"
              value={stats.avgTime > 0 ? `${stats.avgTime}d` : "N/A"}
              icon={<Timer className="h-5 w-5 text-primary" />}
            />
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex items-center justify-between">
          <div className="flex gap-3">
            <Button onClick={() => router.push("/employees?action=add")}>
              <Plus className="mr-2 h-4 w-4" />
              Add New Employee
            </Button>
            <Button variant="outline" onClick={() => router.push("/employees?action=upload")}>
              <Upload className="mr-2 h-4 w-4" />
              Upload CSV
            </Button>
          </div>
          <Link
            href="/employees"
            className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
          >
            View All Employees
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>

        {/* Recent Activity Table */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-3">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-12" />
                ))}
              </div>
            ) : recentEmployees.length === 0 ? (
              <div className="py-8 text-center text-muted-foreground">
                No employees yet. Add your first employee to get started.
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Employee</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Current Step</TableHead>
                    <TableHead>Started</TableHead>
                    <TableHead className="w-12">Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {recentEmployees.map((employee) => (
                    <TableRow key={employee.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium">{employee.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {employee.email}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={employee.status} />
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {getStepLabel(employee.status)}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {employee.status === "pending"
                          ? "—"
                          : formatTimeAgo(employee.updated_at)}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => router.push(`/onboarding/${employee.id}`)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Bottom Section: Compliance Alerts + Pending Approvals */}
        <div className="grid gap-6 md:grid-cols-2">
          {/* Compliance Alerts */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-base">
                <ShieldAlert className="h-4 w-4 text-yellow-500" />
                Compliance Alerts
              </CardTitle>
              <Link
                href="/compliance"
                className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
              >
                View All
                <ArrowRight className="h-3 w-3" />
              </Link>
            </CardHeader>
            <CardContent>
              {complianceAlerts.length === 0 ? (
                <div className="py-4 text-center text-sm text-muted-foreground">
                  <CheckCircle className="mx-auto mb-2 h-6 w-6 text-green-500" />
                  No compliance alerts
                </div>
              ) : (
                <div className="space-y-3">
                  {complianceAlerts.slice(0, 4).map((alert) => (
                    <div
                      key={alert.id}
                      className="flex items-center justify-between rounded-lg border p-3"
                    >
                      <div className="flex items-center gap-2">
                        {alert.status === "expired" ? (
                          <XCircle className="h-4 w-4 text-red-500 shrink-0" />
                        ) : (
                          <AlertTriangle className="h-4 w-4 text-yellow-500 shrink-0" />
                        )}
                        <div>
                          <p className="text-sm font-medium">{alert.description}</p>
                          <p className="text-xs text-muted-foreground">{alert.employee_name}</p>
                        </div>
                      </div>
                      <Badge
                        variant={alert.status === "expired" ? "destructive" : "outline"}
                        className={
                          alert.status === "expiring_soon"
                            ? "border-yellow-500/50 text-yellow-500"
                            : ""
                        }
                      >
                        {alert.status === "expired" ? "Expired" : "Expiring"}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Pending Approvals */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-base">
                <CheckSquare className="h-4 w-4 text-primary" />
                Pending Approvals
              </CardTitle>
              <Link
                href="/approvals"
                className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
              >
                View All
                <ArrowRight className="h-3 w-3" />
              </Link>
            </CardHeader>
            <CardContent>
              {pendingApprovals === 0 ? (
                <div className="py-4 text-center text-sm text-muted-foreground">
                  <CheckCircle className="mx-auto mb-2 h-6 w-6 text-green-500" />
                  No pending approvals
                </div>
              ) : (
                <div className="flex flex-col items-center py-4">
                  <div className="text-4xl font-bold text-primary">{pendingApprovals}</div>
                  <p className="text-sm text-muted-foreground mt-1">documents awaiting review</p>
                  <Button
                    className="mt-4"
                    size="sm"
                    onClick={() => router.push("/approvals")}
                  >
                    Review Now
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
