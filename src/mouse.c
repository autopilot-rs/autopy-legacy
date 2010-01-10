#include "mouse.h"
#include "screen.h"
#include "keywords.h"
#include "deadbeef_rand.h"
#include "math.h" /* hypot() */

#if defined(IS_MACOSX)
	#include <ApplicationServices/ApplicationServices.h>
#elif defined(USE_X11)
	#include <X11/Xlib.h>
	#include <X11/extensions/XTest.h>
	#include "xdisplay.h"
#endif

#if defined(IS_WINDOWS)
	#define usleep(x) Sleep((x) / 1000)
	#define lround(x) (long int)floor(x + 0.5)
#else
	#include <unistd.h> /* For usleep() */
#endif

#if defined(_MSC_VER)
	#define ssize_t SSIZE_T /* sigh */
#endif

INLINE void moveMouse(MMPoint point)
{
#if defined(IS_MACOSX)
	CGEventRef move = CGEventCreateMouseEvent(NULL, kCGEventMouseMoved,
	                                          CGPointFromMMPoint(point),
	                                          0);
	CGEventPost(kCGSessionEventTap, move);
	CFRelease(move);
#elif defined(USE_X11)
	Display *display = XGetMainDisplay();
	XWarpPointer(display, None, DefaultRootWindow(display),
	             0, 0, 0, 0, point.x, point.y);
	XFlush(display);
#elif defined(IS_WINDOWS)
	mouse_event(MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE,
	            point.x, point.y, 0, 0);
#endif
}

INLINE MMPoint getMousePos()
{
#if defined(IS_MACOSX)
	CGEventRef event = CGEventCreate(NULL);
	CGPoint point = CGEventGetLocation(event);
	CFRelease(event);

	return MMPointFromCGPoint(point);
#elif defined(USE_X11)
	int x, y; /* This is all we care about. Seriously. */
	Window garb1, garb2; /* Why you can't specify NULL as a parameter */
	int garb_x, garb_y;  /* is beyond me. */
	unsigned int more_garbage;

	Display *display = XGetMainDisplay();
	XQueryPointer(display, XDefaultRootWindow(display), &garb1, &garb2,
	              &x, &y, &garb_x, &garb_y, &more_garbage);

	return MMPointMake(x, y);
#elif defined(IS_WINDOWS)
	POINT point;
	GetCursorPos(&point);

	return MMPointFromPOINT(point);
#endif
}

/* Some convenience macros for converting our enums to the system API types. */
#if defined(IS_MACOSX)

#define MMMouseToCGEventType(down, button) \
	(down ? MMMouseDownToCGEventType(button) : MMMouseUpToCGEventType(button))

#define MMMouseDownToCGEventType(button) \
	((button) == (LEFT_BUTTON) ? kCGEventLeftMouseDown \
	                       : ((button) == RIGHT_BUTTON ? kCGEventRightMouseDown \
	                                                   : kCGEventOtherMouseDown))

#define MMMouseUpToCGEventType(button) \
	((button) == LEFT_BUTTON ? kCGEventLeftMouseUp \
	                         : ((button) == RIGHT_BUTTON ? kCGEventRightMouseUp \
	                                                     : kCGEventOtherMouseUp))

#elif defined(IS_WINDOWS)

#define MMMouseToMEventF(down, button) \
	(down ? MMMouseDownToMEventF(button) : MMMouseUpToMEventF(button))

#define MMMouseUpToMEventF(button) \
	((button) == LEFT_BUTTON ? MOUSEEVENTF_LEFTUP \
	                         : ((button) == RIGHT_BUTTON ? MOUSEEVENTF_RIGHTUP \
	                                                     : MOUSEEVENTF_MIDDLEUP))

#define MMMouseDownToMEventF(button) \
	((button) == LEFT_BUTTON ? MOUSEEVENTF_LEFTDOWN \
	                         : ((button) == RIGHT_BUTTON ? MOUSEEVENTF_RIGHTDOWN \
	                                                     : MOUSEEVENTF_MIDDLEDOWN))

#endif

INLINE void toggleMouse(bool down, MMMouseButton button)
{
#if defined(IS_MACOSX)
	const CGPoint currentPos = CGPointFromMMPoint(getMousePos());
	const CGEventType mouseType = MMMouseToCGEventType(down, button);
	CGEventRef event = CGEventCreateMouseEvent(NULL,
	                                           mouseType,
	                                           currentPos,
	                                           (CGMouseButton)button);
	CGEventPost(kCGSessionEventTap, event);
	CFRelease(event);
#elif defined(USE_X11)
	Display *display = XGetMainDisplay();
	XTestFakeButtonEvent(display, button, down ? True : False, CurrentTime);
	XFlush(display);
#elif defined(IS_WINDOWS)
	mouse_event(MMMouseToMEventF(down, button), 0, 0, 0, 0);
#endif
}

INLINE void clickMouse(MMMouseButton button)
{
	toggleMouse(true, button);
	toggleMouse(false, button);
}

bool smoothlyMoveMouse(MMPoint endPoint)
{
	MMPoint pos = getMousePos();
	MMSize screenSize = getMainDisplaySize();
	double velo_x = 0.0, velo_y = 0.0;
	double distance;

	while ((distance = hypot(pos.x - endPoint.x, pos.y - endPoint.y)) > 1.0) {
		double gravity = DEADBEEF_UNIFORM(5.0, 500.0);
		double veloDistance;
		velo_x += (gravity * (ssize_t)(endPoint.x - pos.x)) / distance;
		velo_y += (gravity * (ssize_t)(endPoint.y - pos.y)) / distance;

		/* Normalize velocity to get a unit vector of length 1. */
		veloDistance = hypot(velo_x, velo_y);
		velo_x /= veloDistance;
		velo_y /= veloDistance;

		pos.x += lround(velo_x);
		pos.y += lround(velo_y);

		/* Make sure we are in the screen boundaries!
		 * (Strange things will happen if we are not.) */
		if (pos.x >= screenSize.width || pos.y >= screenSize.height) {
			return false;
		}

		moveMouse(pos);

		/* Wait 1 - 3 milliseconds. */
		usleep(DEADBEEF_RANDRANGE(1000, 3001));
	}

	return true;
}