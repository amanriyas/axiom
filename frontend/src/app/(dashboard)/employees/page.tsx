"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useDropzone } from "react-dropzone";
import {
  Plus,
  Upload,
  Search,
  MoreHorizontal,
  Eye,
  Pencil,
  Trash2,
  FileSpreadsheet,
  X,
  Loader2,
} from "lucide-react";
import { TopNav } from "@/components/layout/top-nav";
import { StatusBadge } from "@/components/ui/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { employeeApi } from "@/lib/api";
import { Employee, EmployeeCreate, EmployeeUpdate } from "@/types";

const departments = ["Engineering", "Design", "Product", "Marketing", "Sales", "HR", "Finance", "Operations"];

const jurisdictions = [
  { code: "US", name: "United States" },
  { code: "UK", name: "United Kingdom" },
  { code: "AE", name: "UAE" },
  { code: "DE", name: "Germany" },
  { code: "SG", name: "Singapore" },
];

export default function EmployeesPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [departmentFilter, setDepartmentFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  // Dialog states
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [employeeToEdit, setEmployeeToEdit] = useState<Employee | null>(null);
  const [employeeToDelete, setEmployeeToDelete] = useState<Employee | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form state for Add
  const [formData, setFormData] = useState<EmployeeCreate>({
    name: "",
    email: "",
    role: "",
    department: "",
    start_date: "",
    manager_email: "",
    buddy_email: "",
  });

  // Form state for Edit
  const [editFormData, setEditFormData] = useState<EmployeeUpdate>({
    name: "",
    email: "",
    role: "",
    department: "",
    start_date: "",
    manager_email: "",
    buddy_email: "",
  });

  // CSV upload state
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState<{
    total: number;
    created: number;
    errors: string[];
  } | null>(null);

  useEffect(() => {
    fetchEmployees();
  }, []);

  useEffect(() => {
    const action = searchParams.get("action");
    if (action === "add") {
      setAddDialogOpen(true);
    } else if (action === "upload") {
      setUploadDialogOpen(true);
    }
  }, [searchParams]);

  const fetchEmployees = async () => {
    try {
      const data = await employeeApi.list();
      setEmployees(data);
    } catch (error) {
      console.error("Failed to fetch employees:", error);
      toast.error("Failed to load employees");
    } finally {
      setLoading(false);
    }
  };

  const handleAddEmployee = async () => {
    if (!formData.name || !formData.email || !formData.role || !formData.department || !formData.start_date) {
      toast.error("Please fill in all required fields");
      return;
    }

    setIsSubmitting(true);
    try {
      await employeeApi.create(formData);
      toast.success("Employee added successfully");
      setAddDialogOpen(false);
      setFormData({
        name: "",
        email: "",
        role: "",
        department: "",
        start_date: "",
        manager_email: "",
        buddy_email: "",
      });
      fetchEmployees();
      router.replace("/employees");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to add employee";
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteEmployee = async () => {
    if (!employeeToDelete) return;

    setIsSubmitting(true);
    try {
      await employeeApi.delete(employeeToDelete.id);
      toast.success("Employee deleted successfully");
      setDeleteDialogOpen(false);
      setEmployeeToDelete(null);
      fetchEmployees();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to delete employee";
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const openEditDialog = (employee: Employee) => {
    setEmployeeToEdit(employee);
    setEditFormData({
      name: employee.name,
      email: employee.email,
      role: employee.role,
      department: employee.department,
      start_date: employee.start_date,
      manager_email: employee.manager_email || "",
      buddy_email: employee.buddy_email || "",
      jurisdiction: employee.jurisdiction || "US",
    });
    setEditDialogOpen(true);
  };

  const closeEditDialog = () => {
    setEditDialogOpen(false);
    setEmployeeToEdit(null);
    setEditFormData({
      name: "",
      email: "",
      role: "",
      department: "",
      start_date: "",
      manager_email: "",
      buddy_email: "",
    });
  };

  const handleEditEmployee = async () => {
    if (!employeeToEdit) return;

    if (!editFormData.name || !editFormData.email || !editFormData.role || !editFormData.department || !editFormData.start_date) {
      toast.error("Please fill in all required fields");
      return;
    }

    setIsSubmitting(true);
    try {
      await employeeApi.update(employeeToEdit.id, editFormData);
      toast.success("Employee updated successfully");
      closeEditDialog();
      fetchEmployees();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to update employee";
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setCsvFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "text/csv": [".csv"] },
    maxFiles: 1,
  });

  const handleUploadCsv = async () => {
    if (!csvFile) return;

    setIsSubmitting(true);
    try {
      const result = await employeeApi.uploadCsv(csvFile);
      setUploadProgress(result);
      if (result.created > 0) {
        toast.success(`Successfully imported ${result.created} employees`);
        fetchEmployees();
      }
      if (result.errors.length > 0) {
        toast.error(`${result.errors.length} rows had errors`);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to upload CSV";
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const closeUploadDialog = () => {
    setUploadDialogOpen(false);
    setCsvFile(null);
    setUploadProgress(null);
    router.replace("/employees");
  };

  const closeAddDialog = () => {
    setAddDialogOpen(false);
    setFormData({
      name: "",
      email: "",
      role: "",
      department: "",
      start_date: "",
      manager_email: "",
      buddy_email: "",
    });
    router.replace("/employees");
  };

  // Filter employees
  const filteredEmployees = employees.filter((emp) => {
    const matchesSearch =
      emp.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      emp.email.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesDepartment = departmentFilter === "all" || emp.department === departmentFilter;
    const matchesStatus = statusFilter === "all" || emp.status === statusFilter;
    return matchesSearch && matchesDepartment && matchesStatus;
  });

  return (
    <div className="flex flex-col">
      <TopNav title="Employees" />

      <div className="flex-1 space-y-6 p-6">
        {/* Header Actions */}
        <div className="flex items-center justify-between">
          <div className="flex gap-3">
            <Button onClick={() => setAddDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Add Employee
            </Button>
            <Button variant="outline" onClick={() => setUploadDialogOpen(true)}>
              <Upload className="mr-2 h-4 w-4" />
              Upload CSV
            </Button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search employees..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
          <Select value={departmentFilter} onValueChange={setDepartmentFilter}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="All Departments" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Departments</SelectItem>
              {departments.map((dept) => (
                <SelectItem key={dept} value={dept}>
                  {dept}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="All Statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="onboarding">In Progress</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="failed">Failed</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Employees Table */}
        <Card>
          <CardContent className="p-0">
            {loading ? (
              <div className="space-y-3 p-6">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-16" />
                ))}
              </div>
            ) : filteredEmployees.length === 0 ? (
              <div className="py-12 text-center text-muted-foreground">
                {employees.length === 0
                  ? "No employees yet. Add your first employee to get started."
                  : "No employees match your filters."}
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Department</TableHead>
                    <TableHead>Jurisdiction</TableHead>
                    <TableHead>Start Date</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="w-12"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredEmployees.map((employee) => (
                    <TableRow key={employee.id}>
                      <TableCell className="font-medium">{employee.name}</TableCell>
                      <TableCell className="text-muted-foreground">{employee.email}</TableCell>
                      <TableCell>{employee.role}</TableCell>
                      <TableCell>{employee.department}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="font-mono text-xs">
                          {employee.jurisdiction || "US"}
                        </Badge>
                      </TableCell>
                      <TableCell>{new Date(employee.start_date).toLocaleDateString()}</TableCell>
                      <TableCell>
                        <StatusBadge status={employee.status} />
                      </TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem
                              onClick={() => router.push(`/onboarding/${employee.id}`)}
                            >
                              <Eye className="mr-2 h-4 w-4" />
                              View Onboarding
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => openEditDialog(employee)}>
                              <Pencil className="mr-2 h-4 w-4" />
                              Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              className="text-destructive"
                              onClick={() => {
                                setEmployeeToDelete(employee);
                                setDeleteDialogOpen(true);
                              }}
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Add Employee Dialog */}
      <Dialog open={addDialogOpen} onOpenChange={closeAddDialog}>
        <DialogContent className="max-w-md max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Add New Employee</DialogTitle>
            <DialogDescription>
              Enter the employee details to start onboarding.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="John Doe"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email *</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="john@company.com"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="role">Role *</Label>
              <Input
                id="role"
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                placeholder="Senior Engineer"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="department">Department *</Label>
              <Select
                value={formData.department}
                onValueChange={(value) => setFormData({ ...formData, department: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select department" />
                </SelectTrigger>
                <SelectContent>
                  {departments.map((dept) => (
                    <SelectItem key={dept} value={dept}>
                      {dept}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="start_date">Start Date *</Label>
              <Input
                id="start_date"
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="jurisdiction">Jurisdiction</Label>
              <Select
                value={formData.jurisdiction || "US"}
                onValueChange={(value) => setFormData({ ...formData, jurisdiction: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select jurisdiction" />
                </SelectTrigger>
                <SelectContent>
                  {jurisdictions.map((j) => (
                    <SelectItem key={j.code} value={j.code}>
                      {j.name} ({j.code})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="manager_email">Manager Email</Label>
              <Input
                id="manager_email"
                type="email"
                value={formData.manager_email || ""}
                onChange={(e) => setFormData({ ...formData, manager_email: e.target.value })}
                placeholder="manager@company.com"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="buddy_email">Buddy Email</Label>
              <Input
                id="buddy_email"
                type="email"
                value={formData.buddy_email || ""}
                onChange={(e) => setFormData({ ...formData, buddy_email: e.target.value })}
                placeholder="buddy@company.com"
              />
            </div>
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={closeAddDialog}>
                Cancel
              </Button>
              <Button onClick={handleAddEmployee} disabled={isSubmitting}>
                {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Add Employee
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Edit Employee Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={closeEditDialog}>
        <DialogContent className="max-w-md max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Employee</DialogTitle>
            <DialogDescription>
              Update the employee details.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="edit-name">Name *</Label>
              <Input
                id="edit-name"
                value={editFormData.name || ""}
                onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })}
                placeholder="John Doe"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-email">Email *</Label>
              <Input
                id="edit-email"
                type="email"
                value={editFormData.email || ""}
                onChange={(e) => setEditFormData({ ...editFormData, email: e.target.value })}
                placeholder="john@company.com"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-role">Role *</Label>
              <Input
                id="edit-role"
                value={editFormData.role || ""}
                onChange={(e) => setEditFormData({ ...editFormData, role: e.target.value })}
                placeholder="Senior Engineer"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-department">Department *</Label>
              <Select
                value={editFormData.department || ""}
                onValueChange={(value) => setEditFormData({ ...editFormData, department: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select department" />
                </SelectTrigger>
                <SelectContent>
                  {departments.map((dept) => (
                    <SelectItem key={dept} value={dept}>
                      {dept}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-start_date">Start Date *</Label>
              <Input
                id="edit-start_date"
                type="date"
                value={editFormData.start_date || ""}
                onChange={(e) => setEditFormData({ ...editFormData, start_date: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-jurisdiction">Jurisdiction</Label>
              <Select
                value={editFormData.jurisdiction || "US"}
                onValueChange={(value) => setEditFormData({ ...editFormData, jurisdiction: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select jurisdiction" />
                </SelectTrigger>
                <SelectContent>
                  {jurisdictions.map((j) => (
                    <SelectItem key={j.code} value={j.code}>
                      {j.name} ({j.code})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-manager_email">Manager Email</Label>
              <Input
                id="edit-manager_email"
                type="email"
                value={editFormData.manager_email || ""}
                onChange={(e) => setEditFormData({ ...editFormData, manager_email: e.target.value })}
                placeholder="manager@company.com"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-buddy_email">Buddy Email</Label>
              <Input
                id="edit-buddy_email"
                type="email"
                value={editFormData.buddy_email || ""}
                onChange={(e) => setEditFormData({ ...editFormData, buddy_email: e.target.value })}
                placeholder="buddy@company.com"
              />
            </div>
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={closeEditDialog}>
                Cancel
              </Button>
              <Button onClick={handleEditEmployee} disabled={isSubmitting}>
                {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Save Changes
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Upload CSV Dialog */}
      <Dialog open={uploadDialogOpen} onOpenChange={closeUploadDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Upload Employee CSV</DialogTitle>
            <DialogDescription>
              Import multiple employees from a CSV file.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {!csvFile ? (
              <div
                {...getRootProps()}
                className={`flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 transition-colors ${
                  isDragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25"
                }`}
              >
                <input {...getInputProps()} />
                <FileSpreadsheet className="mb-4 h-12 w-12 text-muted-foreground" />
                <p className="text-center text-sm text-muted-foreground">
                  {isDragActive
                    ? "Drop the CSV file here..."
                    : "Drag & drop a CSV file here, or click to browse"}
                </p>
                <p className="mt-2 text-xs text-muted-foreground">
                  CSV files only
                </p>
              </div>
            ) : (
              <div className="rounded-lg border p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <FileSpreadsheet className="h-8 w-8 text-primary" />
                    <div>
                      <p className="font-medium">{csvFile.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {(csvFile.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => {
                      setCsvFile(null);
                      setUploadProgress(null);
                    }}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}

            {uploadProgress && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Upload Results</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <p>Total rows: {uploadProgress.total}</p>
                  <p className="text-[#22c55e]">Created: {uploadProgress.created}</p>
                  {uploadProgress.errors.length > 0 && (
                    <div>
                      <p className="text-[#ef4444]">Errors: {uploadProgress.errors.length}</p>
                      <ul className="mt-1 max-h-32 overflow-auto text-xs text-muted-foreground">
                        {uploadProgress.errors.map((err, i) => (
                          <li key={i}>{err}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={closeUploadDialog}>
                {uploadProgress ? "Close" : "Cancel"}
              </Button>
              {!uploadProgress && (
                <Button onClick={handleUploadCsv} disabled={!csvFile || isSubmitting}>
                  {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Upload
                </Button>
              )}
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Employee</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete {employeeToDelete?.name}? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteEmployee}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isSubmitting ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : null}
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
