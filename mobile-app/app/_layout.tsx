import { DrawerContentScrollView, DrawerItem, DrawerItemList } from "@react-navigation/drawer";
import Home from "app";
import { Stack } from "expo-router";
import { NativeWindStyleSheet } from "nativewind";

NativeWindStyleSheet.setOutput({
    default: "native",
});

export default function Layout() {
    return (
        <Stack
            screenOptions={{
                headerShown: false,
            }}
        >
            <Stack.Screen name="index" />
        </Stack>
    );
}
