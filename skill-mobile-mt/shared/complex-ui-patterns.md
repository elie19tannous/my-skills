# Complex UI Patterns — Production Templates

> On-demand module. Loaded when building carousels, gestures, responsive layouts, keyboard handling, or dark mode.
> Contains runnable code templates for complex UI scenarios.

---

## Image Carousel with Snap + Indicators

### React Native (FlatList)

```typescript
// components/ImageCarousel.tsx
import { FlatList, Dimensions, View, Image, StyleSheet } from 'react-native';
import { useState, useRef, useCallback } from 'react';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

interface Props {
  images: string[];
  height?: number;
}

export function ImageCarousel({ images, height = 300 }: Props) {
  const [activeIndex, setActiveIndex] = useState(0);
  const flatListRef = useRef<FlatList>(null);

  const onViewableItemsChanged = useCallback(({ viewableItems }: { viewableItems: Array<{ index: number | null }> }) => {
    if (viewableItems[0]?.index != null) setActiveIndex(viewableItems[0].index);
  }, []);

  const viewabilityConfig = useRef({ viewAreaCoveragePercentThreshold: 50 }).current;

  return (
    <View>
      <FlatList
        ref={flatListRef}
        data={images}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onViewableItemsChanged={onViewableItemsChanged}
        viewabilityConfig={viewabilityConfig}
        keyExtractor={(_, i) => `img-${i}`}
        renderItem={({ item }) => (
          <Image
            source={{ uri: item }}
            style={{ width: SCREEN_WIDTH, height }}
            resizeMode="cover"
          />
        )}
        getItemLayout={(_, index) => ({
          length: SCREEN_WIDTH,
          offset: SCREEN_WIDTH * index,
          index,
        })}
      />
      {/* Indicators */}
      <View style={styles.indicators}>
        {images.map((_, i) => (
          <View
            key={i}
            style={[styles.dot, i === activeIndex && styles.dotActive]}
          />
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  indicators: { flexDirection: 'row', justifyContent: 'center', paddingVertical: 8 },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#ccc', marginHorizontal: 4 },
  dotActive: { backgroundColor: '#333', width: 24 },
});
```

### Flutter

```dart
// widgets/image_carousel.dart
class ImageCarousel extends StatefulWidget {
  final List<String> images;
  final double height;
  const ImageCarousel({required this.images, this.height = 300, super.key});

  @override
  State<ImageCarousel> createState() => _ImageCarouselState();
}

class _ImageCarouselState extends State<ImageCarousel> {
  int _current = 0;
  final _controller = PageController();

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SizedBox(
          height: widget.height,
          child: PageView.builder(
            controller: _controller,
            onPageChanged: (i) => setState(() => _current = i),
            itemCount: widget.images.length,
            itemBuilder: (_, i) => Image.network(widget.images[i], fit: BoxFit.cover),
          ),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(widget.images.length, (i) => AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            width: _current == i ? 24 : 8,
            height: 8,
            margin: const EdgeInsets.symmetric(horizontal: 4),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(4),
              color: _current == i ? Colors.black : Colors.grey[300],
            ),
          )),
        ),
      ],
    );
  }
}
```

---

## Gesture Handling

### React Native (Reanimated + Gesture Handler)

```typescript
// components/SwipeableCard.tsx — Swipe left to delete, right to archive
import Animated, { useSharedValue, useAnimatedStyle, withSpring, runOnJS } from 'react-native-reanimated';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';

interface Props {
  children: React.ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  threshold?: number;
}

export function SwipeableCard({ children, onSwipeLeft, onSwipeRight, threshold = 100 }: Props) {
  const translateX = useSharedValue(0);

  const panGesture = Gesture.Pan()
    .onUpdate((e) => {
      translateX.value = e.translationX;
    })
    .onEnd((e) => {
      if (e.translationX < -threshold && onSwipeLeft) {
        runOnJS(onSwipeLeft)();
      } else if (e.translationX > threshold && onSwipeRight) {
        runOnJS(onSwipeRight)();
      }
      translateX.value = withSpring(0);
    });

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }],
  }));

  return (
    <GestureDetector gesture={panGesture}>
      <Animated.View style={animatedStyle}>
        {children}
      </Animated.View>
    </GestureDetector>
  );
}

// Long Press with Haptic
import * as Haptics from 'expo-haptics';

const longPressGesture = Gesture.LongPress()
  .minDuration(500)
  .onStart(() => {
    runOnJS(Haptics.impactAsync)(Haptics.ImpactFeedbackStyle.Medium);
    runOnJS(onLongPress)();
  });
```

---

## Keyboard Handling

### React Native — Keyboard Avoidance

```typescript
// components/KeyboardAwareView.tsx
import { KeyboardAvoidingView, Platform, TouchableWithoutFeedback, Keyboard } from 'react-native';

interface Props {
  children: React.ReactNode;
}

export function KeyboardAwareView({ children }: Props) {
  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={{ flex: 1 }}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 64 : 0} // adjust for header
    >
      <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
        <View style={{ flex: 1 }}>
          {children}
        </View>
      </TouchableWithoutFeedback>
    </KeyboardAvoidingView>
  );
}

// For ScrollView forms — use KeyboardAwareScrollView
// npm: react-native-keyboard-aware-scroll-view
import { KeyboardAwareScrollView } from 'react-native-keyboard-aware-scroll-view';

function FormScreen() {
  return (
    <KeyboardAwareScrollView
      extraScrollHeight={20}
      enableOnAndroid
      keyboardShouldPersistTaps="handled"
    >
      {/* form fields */}
    </KeyboardAwareScrollView>
  );
}
```

---

## Responsive Layout

### React Native — Tablet + Landscape Support

```typescript
// hooks/useResponsive.ts
import { useWindowDimensions } from 'react-native';

type Breakpoint = 'phone' | 'tablet' | 'desktop';

export function useResponsive() {
  const { width, height } = useWindowDimensions();

  const breakpoint: Breakpoint = width >= 1024 ? 'desktop' : width >= 768 ? 'tablet' : 'phone';
  const isLandscape = width > height;
  const numColumns = breakpoint === 'phone' ? 1 : breakpoint === 'tablet' ? 2 : 3;

  return { width, height, breakpoint, isLandscape, numColumns };
}

// Usage in list screen:
function ProductListScreen() {
  const { numColumns } = useResponsive();

  return (
    <FlatList
      data={products}
      numColumns={numColumns}
      key={`cols-${numColumns}`} // force re-render on column change
      renderItem={({ item }) => (
        <View style={{ flex: 1 / numColumns, padding: 8 }}>
          <ProductCard product={item} />
        </View>
      )}
    />
  );
}
```

### Flutter — Responsive Layout

```dart
// widgets/responsive_layout.dart
class ResponsiveLayout extends StatelessWidget {
  final Widget phone;
  final Widget? tablet;
  const ResponsiveLayout({required this.phone, this.tablet, super.key});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(builder: (context, constraints) {
      if (constraints.maxWidth >= 768 && tablet != null) return tablet!;
      return phone;
    });
  }
}

// Usage:
ResponsiveLayout(
  phone: ProductListView(columns: 1),
  tablet: ProductGridView(columns: 3),
)
```

---

## Dark Mode Implementation

### React Native — Theme System

```typescript
// theme/ThemeProvider.tsx
import { createContext, useContext, useMemo } from 'react';
import { useColorScheme } from 'react-native';

const lightColors = {
  background: '#FFFFFF',
  surface: '#F5F5F5',
  text: '#1A1A1A',
  textSecondary: '#666666',
  primary: '#007AFF',
  border: '#E0E0E0',
  error: '#FF3B30',
};

const darkColors = {
  background: '#000000',    // OLED black
  surface: '#1C1C1E',
  text: '#FFFFFF',
  textSecondary: '#8E8E93',
  primary: '#0A84FF',
  border: '#38383A',
  error: '#FF453A',
};

type ThemeColors = typeof lightColors;

interface Theme {
  colors: ThemeColors;
  isDark: boolean;
}

const ThemeContext = createContext<Theme>({} as Theme);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const colorScheme = useColorScheme();
  const theme = useMemo<Theme>(() => ({
    colors: colorScheme === 'dark' ? darkColors : lightColors,
    isDark: colorScheme === 'dark',
  }), [colorScheme]);

  return <ThemeContext.Provider value={theme}>{children}</ThemeContext.Provider>;
}

export const useTheme = () => useContext(ThemeContext);

// Usage in any component:
// const { colors, isDark } = useTheme();
// <View style={{ backgroundColor: colors.background }}>
//   <Text style={{ color: colors.text }}>Hello</Text>
// </View>
```

### Flutter — Theme Switching

```dart
// theme/app_theme.dart
class AppTheme {
  static ThemeData light = ThemeData(
    brightness: Brightness.light,
    colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
    useMaterial3: true,
  );

  static ThemeData dark = ThemeData(
    brightness: Brightness.dark,
    colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue, brightness: Brightness.dark),
    scaffoldBackgroundColor: Colors.black, // OLED
    useMaterial3: true,
  );
}

// main.dart
MaterialApp(
  theme: AppTheme.light,
  darkTheme: AppTheme.dark,
  themeMode: ThemeMode.system, // or ThemeMode.dark / ThemeMode.light
)
```

---

## Accessibility Implementation

### React Native

```typescript
// Accessible button with proper semantics
<TouchableOpacity
  accessible
  accessibilityRole="button"
  accessibilityLabel="Add to cart"
  accessibilityHint="Double tap to add this product to your shopping cart"
  accessibilityState={{ disabled: !inStock }}
  onPress={handleAddToCart}
  style={[styles.button, !inStock && styles.buttonDisabled]}
>
  <Text style={styles.buttonText}>{inStock ? 'Add to Cart' : 'Out of Stock'}</Text>
</TouchableOpacity>

// Image with description
<Image
  source={{ uri: product.images[0] }}
  accessible
  accessibilityLabel={`Product image: ${product.title}`}
  accessibilityRole="image"
/>

// Live region for dynamic content (screen reader announces changes)
<Text accessibilityLiveRegion="polite">
  {cartCount} items in cart
</Text>

// Minimum touch target: 44x44 points (iOS HIG) / 48x48 dp (Material)
const styles = StyleSheet.create({
  touchTarget: {
    minWidth: 44,
    minHeight: 44,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
```

### Flutter

```dart
// Accessible widget
Semantics(
  label: 'Add to cart',
  hint: 'Double tap to add this product to your shopping cart',
  button: true,
  enabled: inStock,
  child: ElevatedButton(
    onPressed: inStock ? onAddToCart : null,
    child: Text(inStock ? 'Add to Cart' : 'Out of Stock'),
  ),
)

// Image with semantics
Semantics(
  image: true,
  label: 'Product image: ${product.title}',
  child: Image.network(product.images[0]),
)
```

### iOS SwiftUI

```swift
Button(action: addToCart) {
    Text(inStock ? "Add to Cart" : "Out of Stock")
}
.disabled(!inStock)
.accessibilityLabel("Add to cart")
.accessibilityHint("Double tap to add this product to your shopping cart")
```

### Android Compose

```kotlin
Button(
    onClick = { addToCart() },
    enabled = inStock,
    modifier = Modifier.semantics {
        contentDescription = "Add to cart"
    }
) {
    Text(if (inStock) "Add to Cart" else "Out of Stock")
}
```

---

## Skeleton Loading

### React Native — Shimmer Skeleton

```typescript
// components/Skeleton.tsx
import Animated, { useSharedValue, useAnimatedStyle, withRepeat, withTiming } from 'react-native-reanimated';
import { useEffect } from 'react';
import { useTheme } from '@/theme/ThemeProvider';

interface Props {
  width: number | `${number}%`;
  height: number;
  borderRadius?: number;
}

export function Skeleton({ width, height, borderRadius = 4 }: Props) {
  const { colors } = useTheme();
  const opacity = useSharedValue(0.3);

  useEffect(() => {
    opacity.value = withRepeat(withTiming(1, { duration: 800 }), -1, true);
  }, []);

  const style = useAnimatedStyle(() => ({ opacity: opacity.value }));

  return (
    <Animated.View
      style={[{ width, height, borderRadius, backgroundColor: colors.border }, style]}
    />
  );
}

// ProductDetailSkeleton.tsx
export function ProductDetailSkeleton() {
  return (
    <View style={{ padding: 16 }}>
      <Skeleton width="100%" height={300} borderRadius={12} />
      <View style={{ height: 16 }} />
      <Skeleton width="70%" height={24} />
      <View style={{ height: 8 }} />
      <Skeleton width="30%" height={20} />
      <View style={{ height: 16 }} />
      <Skeleton width="100%" height={80} />
    </View>
  );
}
```
