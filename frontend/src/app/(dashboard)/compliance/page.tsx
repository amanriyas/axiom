"use client";

import { useEffect, useState } from "react";
import {
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  Clock,
  CheckCircle,
  XCircle,
  TrendingUp,
} from "lucide-react";
import { TopNav } from "@/components/layout/top-nav";
import { StatsCard } from "@/components/ui/stats-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { complianceApi } from "@/lib/api";
import { ComplianceItem, ComplianceSummary, CompliancePrediction, ComplianceStatus } from "@/types";

function getComplianceBadge(status: ComplianceStatus) {
  switch (status) {
    case "valid":
      return <Badge className="bg-green-500/10 text-green-500 border-green-500/50"><CheckCircle className="mr-1 h-3 w-3" />Valid</Badge>;
    case "expiring_soon":
      return <Badge variant="outline" className="border-yellow-500/50 text-yellow-500"><AlertTriangle className="mr-1 h-3 w-3" />Expiring Soon</Badge>;
    case "expired":
      return <Badge variant="destructive"><XCircle className="mr-1 h-3 w-3" />Expired</Badge>;
    case "pending":
      return <Badge variant="outline"><Clock className="mr-1 h-3 w-3" />Pending</Badge>;
    default:
      return <Badge variant="outline">{status}</Badge>;
  }
}

function getRiskBadge(level: string) {
  switch (level) {
    case "critical":
      return <Badge variant="destructive">Critical</Badge>;
    case "high":
      return <Badge className="bg-orange-500/10 text-orange-500 border-orange-500/50">High</Badge>;
    case "medium":
      return <Badge variant="outline" className="border-yellow-500/50 text-yellow-500">Medium</Badge>;
    case "low":
      return <Badge variant="outline" className="text-green-500 border-green-500/50">Low</Badge>;
    default:
      return <Badge variant="outline">{level}</Badge>;
  }
}

export default function CompliancePage() {
  const [items, setItems] = useState<ComplianceItem[]>([]);
  const [summary, setSummary] = useState<ComplianceSummary | null>(null);
  const [predictions, setPredictions] = useState<CompliancePrediction[]>([]);
  const [alerts, setAlerts] = useState<ComplianceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    fetchAll();
  }, []);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [itemsData, summaryData, predictionsData, alertsData] = await Promise.all([
        complianceApi.list(),
        complianceApi.getSummary(),
        complianceApi.getPredictions(),
        complianceApi.getAlerts(),
      ]);
      setItems(itemsData);
      setSummary(summaryData);
      setPredictions(predictionsData);
      setAlerts(alertsData);
    } catch (error) {
      console.error("Failed to fetch compliance data:", error);
      toast.error("Failed to load compliance data");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col">
      <TopNav title="Compliance" />

      <div className="flex-1 space-y-6 p-6">
        {/* Stats Cards */}
        {loading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
        ) : summary ? (
          <>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <StatsCard
                title="Compliance Rate"
                value={`${summary.total > 0 ? Math.round((summary.valid / summary.total) * 100) : 0}%`}
                icon={<ShieldCheck className="h-5 w-5 text-primary" />}
              />
              <StatsCard
                title="Valid Items"
                value={summary.valid}
                icon={<CheckCircle className="h-5 w-5 text-green-500" />}
              />
              <StatsCard
                title="Expiring Soon"
                value={summary.expiring_soon}
                icon={<AlertTriangle className="h-5 w-5 text-yellow-500" />}
              />
              <StatsCard
                title="Expired"
                value={summary.expired}
                icon={<XCircle className="h-5 w-5 text-red-500" />}
              />
            </div>

            {/* Compliance Progress Bar */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Overall Compliance</CardTitle>
              </CardHeader>
              <CardContent>
                <Progress value={summary.total > 0 ? (summary.valid / summary.total) * 100 : 0} className="h-3" />
                <div className="mt-2 flex justify-between text-xs text-muted-foreground">
                  <span>{summary.valid} valid</span>
                  <span>{summary.expiring_soon} expiring</span>
                  <span>{summary.expired} expired</span>
                  <span>{summary.total - summary.valid - summary.expiring_soon - summary.expired} pending</span>
                </div>
              </CardContent>
            </Card>
          </>
        ) : null}

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="overview">All Items</TabsTrigger>
            <TabsTrigger value="alerts">
              Alerts
              {alerts.length > 0 && (
                <Badge variant="destructive" className="ml-2 h-5 min-w-5 px-1 text-[10px]">
                  {alerts.length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="predictions">
              <TrendingUp className="mr-1 h-3 w-3" />
              Predictions
            </TabsTrigger>
          </TabsList>

          {/* All Items Tab */}
          <TabsContent value="overview">
            <Card>
              <CardContent className="p-0">
                {loading ? (
                  <div className="space-y-3 p-6">
                    {[...Array(5)].map((_, i) => (
                      <Skeleton key={i} className="h-16" />
                    ))}
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Employee</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Title</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Expiry Date</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {items.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={5} className="py-8 text-center text-muted-foreground">
                            No compliance items tracked yet
                          </TableCell>
                        </TableRow>
                      ) : (
                        items.map((item) => (
                          <TableRow key={item.id}>
                            <TableCell className="font-medium">
                              {item.employee_name || `Employee #${item.employee_id}`}
                            </TableCell>
                            <TableCell>
                              <Badge variant="outline" className="font-mono text-xs">
                                {item.item_type}
                              </Badge>
                            </TableCell>
                            <TableCell>{item.description}</TableCell>
                            <TableCell>{getComplianceBadge(item.status)}</TableCell>
                            <TableCell className="text-muted-foreground">
                              {item.expiry_date
                                ? new Date(item.expiry_date).toLocaleDateString()
                                : "N/A"}
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Alerts Tab */}
          <TabsContent value="alerts">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <ShieldAlert className="h-5 w-5 text-yellow-500" />
                  Compliance Alerts
                </CardTitle>
              </CardHeader>
              <CardContent>
                {alerts.length === 0 ? (
                  <div className="py-8 text-center text-muted-foreground">
                    <ShieldCheck className="mx-auto mb-2 h-8 w-8 text-green-500" />
                    <p>No compliance alerts — everything looks good!</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {alerts.map((alert) => (
                      <div
                        key={alert.id}
                        className="flex items-center justify-between rounded-lg border p-4"
                      >
                        <div className="flex items-center gap-3">
                          <AlertTriangle className={`h-5 w-5 ${
                            alert.status === "expired" ? "text-red-500" : "text-yellow-500"
                          }`} />
                          <div>
                            <p className="font-medium text-sm">{alert.description}</p>
                            <p className="text-xs text-muted-foreground">
                              {alert.employee_name} · {alert.item_type}
                              {alert.expiry_date && ` · Expires ${new Date(alert.expiry_date).toLocaleDateString()}`}
                            </p>
                          </div>
                        </div>
                        {getComplianceBadge(alert.status)}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Predictions Tab */}
          <TabsContent value="predictions">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <TrendingUp className="h-5 w-5 text-primary" />
                  Predictive Compliance Alerts
                </CardTitle>
              </CardHeader>
              <CardContent>
                {predictions.length === 0 ? (
                  <div className="py-8 text-center text-muted-foreground">
                    <CheckCircle className="mx-auto mb-2 h-8 w-8 text-green-500" />
                    <p>No upcoming compliance risks detected</p>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Employee</TableHead>
                        <TableHead>Item</TableHead>
                        <TableHead>Expiry</TableHead>
                        <TableHead>Days Left</TableHead>
                        <TableHead>Risk</TableHead>
                        <TableHead>Action</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {predictions.map((pred, i) => (
                        <TableRow key={i}>
                          <TableCell className="font-medium">{pred.employee_name}</TableCell>
                          <TableCell>{pred.description}</TableCell>
                          <TableCell className="text-muted-foreground">
                            {new Date(pred.expiry_date).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            <span className={`font-mono ${
                              pred.days_remaining <= 7 ? "text-red-500" :
                              pred.days_remaining <= 30 ? "text-yellow-500" : ""
                            }`}>
                              {pred.days_remaining}d
                            </span>
                          </TableCell>
                          <TableCell>{getRiskBadge(pred.risk_level)}</TableCell>
                          <TableCell className="text-sm text-muted-foreground max-w-48">
                            {pred.recommended_action}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
