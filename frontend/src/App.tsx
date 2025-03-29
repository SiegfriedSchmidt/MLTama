import {createBrowserRouter, createRoutesFromElements, Route, RouterProvider} from "react-router-dom";
import RootLayout from "./layouts/RootLayout.tsx";
import HomePage from "./pages/HomePage.tsx";
import NotFoundPage from "./pages/NotFoundPage.tsx";
import {useState} from "react";
import {UserData} from "@/types/user.ts";
import {getDefaultUserData} from "@/defaultContext/getDefaultUserData.ts";
import {UserDataContext} from "./context/UserDataContext.tsx";

const router = createBrowserRouter(createRoutesFromElements(
  <Route element={<RootLayout/>}>
    <Route index element={<HomePage/>}/>
    <Route path="*" element={<NotFoundPage/>}/>
  </Route>
))

function App() {
  const [userData, setUserData] = useState<UserData>(getDefaultUserData)

  return (
    <UserDataContext.Provider value={{userData, setUserData}}>
      <RouterProvider router={router}/>
    </UserDataContext.Provider>
  )
}

export default App
