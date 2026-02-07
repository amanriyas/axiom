"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Eye, Play } from "lucide-react";
import { TopNav } from "@/components/layout/top-nav";
import { StatusBadge } from "@/components/ui/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { employeeApi } from "@/lib/api";
import { Employee } from "@/types";

export default function OnboardingListPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchEmployees = async () => {
      try {
        const data = await employeeApi.list();
        setEmployees(data);
      } catch (error) {
        console.error("Failed to fetch employees:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchEmployees();
  }, []);

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
      <TopNav title="Onboarding" />

      <div className="flex-1 space-y-6 p-6">
        <Card>
          <CardContent className="p-0">
            {loading ? (
              <div className="space-y-3 p-6">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-16" />
                ))}
              </div>
            ) : employees.length === 0 ? (
              <div className="py-12 text-center text-muted-foreground">
                No employees yet. Add employees to start onboarding.
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Employee</TableHead>
                    <TableHead>Department</TableHead>
                    <TableHead>Start Date</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Current Step</TableHead>
                    <TableHead className="w-24">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {employees.map((employee) => (
                    <TableRow key={employee.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium">{employee.name}</p>
                          <p className="text-sm text-muted-foreground">{employee.role}</p>
                        </div>
                      </TableCell>
                      <TableCell>{employee.department}</TableCell>
                      <TableCell>
                        {new Date(employee.start_date).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={employee.status} />
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {getStepLabel(employee.status)}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => router.push(`/onboarding/${employee.id}`)}
                          >
                            {employee.status === "pending" ? (
                              <Play className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
