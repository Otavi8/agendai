import { useAuth } from "./context/AuthContext";
import LoginScreen from "./components/LoginScreen";
import ChatScreen from "./components/ChatScreen";

export default function App() {
  const { isAuthenticated } = useAuth();
  return (
    <div className="h-full bg-zinc-50 text-zinc-950">
      {isAuthenticated ? <ChatScreen /> : <LoginScreen />}
    </div>
  );
}
