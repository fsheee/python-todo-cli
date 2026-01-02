// User Types
export interface User {
  id: string;
  email: string;
  name: string;
  image?: string;
}

// Task Types
export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

// Auth Input Types
export interface RegisterInput {
  name: string;
  email: string;
  password: string;
}

export interface LoginInput {
  email: string;
  password: string;
}

export interface ForgotPasswordInput {
  email: string;
}

export interface ResetPasswordInput {
  token: string;
  password: string;
}

// Task Input Types
export interface TaskCreateInput {
  title: string;
  description?: string;
}

export interface TaskUpdateInput {
  title?: string;
  description?: string;
}

// Auth Response Types
export interface AuthResponse {
  user: User;
  token: string;
}

export interface SessionResponse {
  user: User;
  expires_at: string;
}

// Task Response Types
export interface TaskListResponse {
  tasks: Task[];
  count: number;
}

// Error Types
export interface FieldError {
  field: string;
  message: string;
}

export interface ApiError {
  detail: string;
  errors?: FieldError[];
}

// Component Props Types
export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}

export interface InputProps {
  type?: 'text' | 'email' | 'password';
  label: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  className?: string;
  id?: string;
}

export interface CheckboxProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  disabled?: boolean;
  className?: string;
}

export interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
}

export interface ToastType {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

export interface SkeletonProps {
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  className?: string;
}

// Task Component Props
export interface TaskItemProps {
  task: Task;
  onToggle: (id: string) => void;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

export interface TaskListProps {
  tasks: Task[];
  loading?: boolean;
  emptyMessage?: string;
  onToggle: (id: string) => void;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

export interface TaskFormProps {
  mode: 'create' | 'edit';
  initialData?: {
    title: string;
    description?: string;
  };
  onSubmit: (data: TaskCreateInput | TaskUpdateInput) => Promise<void>;
  onCancel?: () => void;
  loading?: boolean;
}

export interface QuickAddTaskProps {
  onAdd: (title: string) => Promise<void>;
  placeholder?: string;
  disabled?: boolean;
}

export interface DeleteConfirmationProps {
  taskTitle: string;
  onConfirm: () => void;
  onCancel: () => void;
  loading?: boolean;
}

// Auth Component Props
export interface SignInFormProps {
  onSubmit: (email: string, password: string) => Promise<void>;
  onForgotPassword: () => void;
  loading?: boolean;
  error?: string;
}

export interface SignUpFormProps {
  onSubmit: (data: RegisterInput) => Promise<void>;
  loading?: boolean;
  error?: string;
}

export interface PasswordRequirementsProps {
  password: string;
}

// Layout Component Props
export interface HeaderProps {
  user?: User | null;
  onSignOut: () => void;
}

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

// Password Validation
export interface PasswordValidation {
  minLength: boolean;
  hasUppercase: boolean;
  hasLowercase: boolean;
  hasNumber: boolean;
}
