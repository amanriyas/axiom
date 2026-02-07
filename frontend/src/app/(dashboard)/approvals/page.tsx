"use client";

import { useEffect, useState } from "react";
import {
  CheckCircle,
  XCircle,
  RotateCcw,
  FileText,
  Clock,
  Loader2,
  Eye,
} from "lucide-react";
import { TopNav } from "@/components/layout/top-nav";
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { approvalApi, documentApi } from "@/lib/api";
import { ApprovalRequest, GeneratedDocument, ApprovalStatus } from "@/types";

function getStatusBadge(status: ApprovalStatus) {
  switch (status) {
    case "pending":
      return <Badge variant="outline" className="border-yellow-500/50 text-yellow-500"><Clock className="mr-1 h-3 w-3" />Pending</Badge>;
    case "approved":
      return <Badge className="bg-green-500/10 text-green-500 border-green-500/50"><CheckCircle className="mr-1 h-3 w-3" />Approved</Badge>;
    case "rejected":
      return <Badge variant="destructive"><XCircle className="mr-1 h-3 w-3" />Rejected</Badge>;
    case "revision_requested":
      return <Badge variant="outline" className="border-orange-500/50 text-orange-500"><RotateCcw className="mr-1 h-3 w-3" />Revision</Badge>;
    default:
      return <Badge variant="outline">{status}</Badge>;
  }
}

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedApproval, setSelectedApproval] = useState<ApprovalRequest | null>(null);
  const [document, setDocument] = useState<GeneratedDocument | null>(null);
  const [reviewDialogOpen, setReviewDialogOpen] = useState(false);
  const [notes, setNotes] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState("pending");

  useEffect(() => {
    fetchApprovals();
  }, []);

  const fetchApprovals = async () => {
    try {
      const data = await approvalApi.list();
      setApprovals(data);
    } catch (error) {
      console.error("Failed to fetch approvals:", error);
      toast.error("Failed to load approvals");
    } finally {
      setLoading(false);
    }
  };

  const openReviewDialog = async (approval: ApprovalRequest) => {
    setSelectedApproval(approval);
    setNotes("");
    setReviewDialogOpen(true);

    // Load the document content
    try {
      const doc = await documentApi.get(approval.document_id);
      setDocument(doc);
    } catch {
      toast.error("Failed to load document");
    }
  };

  const handleAction = async (action: "approve" | "reject" | "revision") => {
    if (!selectedApproval) return;

    setIsSubmitting(true);
    try {
      if (action === "approve") {
        await approvalApi.approve(selectedApproval.id, notes || undefined);
        toast.success("Document approved");
      } else if (action === "reject") {
        await approvalApi.reject(selectedApproval.id, notes || undefined);
        toast.success("Document rejected");
      } else {
        await approvalApi.requestRevision(selectedApproval.id, notes || undefined);
        toast.success("Revision requested");
      }
      setReviewDialogOpen(false);
      setSelectedApproval(null);
      setDocument(null);
      fetchApprovals();
    } catch (error) {
      const message = error instanceof Error ? error.message : `Failed to ${action}`;
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const pendingApprovals = approvals.filter((a) => a.status === "pending");
  const processedApprovals = approvals.filter((a) => a.status !== "pending");

  const renderTable = (items: ApprovalRequest[], showActions: boolean) => (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Employee</TableHead>
          <TableHead>Document</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Submitted</TableHead>
          {showActions && <TableHead className="w-32">Actions</TableHead>}
        </TableRow>
      </TableHeader>
      <TableBody>
        {items.length === 0 ? (
          <TableRow>
            <TableCell colSpan={showActions ? 6 : 5} className="py-8 text-center text-muted-foreground">
              No {showActions ? "pending" : "processed"} approvals
            </TableCell>
          </TableRow>
        ) : (
          items.map((approval) => (
            <TableRow key={approval.id}>
              <TableCell className="font-medium">{approval.employee_name || `Employee #${approval.employee_id}`}</TableCell>
              <TableCell>{approval.document_title || `Doc #${approval.document_id}`}</TableCell>
              <TableCell>
                <Badge variant="outline" className="font-mono text-xs">
                  {(approval.document_type || "unknown").replace(/_/g, " ")}
                </Badge>
              </TableCell>
              <TableCell>{getStatusBadge(approval.status)}</TableCell>
              <TableCell className="text-muted-foreground">
                {new Date(approval.created_at).toLocaleDateString()}
              </TableCell>
              {showActions && (
                <TableCell>
                  <Button size="sm" variant="outline" onClick={() => openReviewDialog(approval)}>
                    <Eye className="mr-1 h-3 w-3" />
                    Review
                  </Button>
                </TableCell>
              )}
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  );

  return (
    <div className="flex flex-col">
      <TopNav title="Approvals" />

      <div className="flex-1 space-y-6 p-6">
        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Pending Review</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{pendingApprovals.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Approved</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-500">
                {approvals.filter((a) => a.status === "approved").length}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Processed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{processedApprovals.length}</div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="pending">
              Pending
              {pendingApprovals.length > 0 && (
                <Badge variant="destructive" className="ml-2 h-5 min-w-5 px-1 text-[10px]">
                  {pendingApprovals.length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="processed">History</TabsTrigger>
          </TabsList>

          <TabsContent value="pending">
            <Card>
              <CardContent className="p-0">
                {loading ? (
                  <div className="space-y-3 p-6">
                    {[...Array(3)].map((_, i) => (
                      <Skeleton key={i} className="h-16" />
                    ))}
                  </div>
                ) : (
                  renderTable(pendingApprovals, true)
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="processed">
            <Card>
              <CardContent className="p-0">
                {loading ? (
                  <div className="space-y-3 p-6">
                    {[...Array(3)].map((_, i) => (
                      <Skeleton key={i} className="h-16" />
                    ))}
                  </div>
                ) : (
                  renderTable(processedApprovals, false)
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Review Dialog */}
      <Dialog open={reviewDialogOpen} onOpenChange={(open) => {
        if (!open) {
          setReviewDialogOpen(false);
          setSelectedApproval(null);
          setDocument(null);
        }
      }}>
        <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Review: {selectedApproval?.document_title || "Document"}
            </DialogTitle>
            <DialogDescription>
              Review this document for {selectedApproval?.employee_name}. You can approve, reject, or request revisions.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* Document Preview */}
            <div className="space-y-2">
              <Label>Document Content</Label>
              <div className="max-h-64 overflow-y-auto rounded-lg border bg-muted/50 p-4 text-sm whitespace-pre-wrap">
                {document ? document.content : "Loading document..."}
              </div>
            </div>

            {/* Reviewer Notes */}
            <div className="space-y-2">
              <Label htmlFor="reviewer-notes">Notes (optional)</Label>
              <Textarea
                id="reviewer-notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add your review comments here..."
                rows={3}
              />
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-2 pt-4">
              <Button
                variant="outline"
                onClick={() => handleAction("revision")}
                disabled={isSubmitting}
              >
                <RotateCcw className="mr-1 h-4 w-4" />
                Request Revision
              </Button>
              <Button
                variant="destructive"
                onClick={() => handleAction("reject")}
                disabled={isSubmitting}
              >
                <XCircle className="mr-1 h-4 w-4" />
                Reject
              </Button>
              <Button
                onClick={() => handleAction("approve")}
                disabled={isSubmitting}
                className="bg-green-600 hover:bg-green-700"
              >
                {isSubmitting ? (
                  <Loader2 className="mr-1 h-4 w-4 animate-spin" />
                ) : (
                  <CheckCircle className="mr-1 h-4 w-4" />
                )}
                Approve
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
