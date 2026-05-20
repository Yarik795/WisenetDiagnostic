import { Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { RecordersProvider } from "./context/RecordersContext";
import { ToastProvider } from "./hooks/useToasts";
import { ObjectsPage } from "./pages/ObjectsPage";
import { RecordersPage } from "./pages/RecordersPage";
import { SettingsPage } from "./pages/SettingsPage";

export default function App() {
  return (
    <ToastProvider>
      <RecordersProvider>
        <Routes>
          <Route element={<AppLayout />}>
            <Route index element={<Navigate to="/objects" replace />} />
            <Route path="objects" element={<ObjectsPage />} />
            <Route path="recorders" element={<RecordersPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </RecordersProvider>
    </ToastProvider>
  );
}
