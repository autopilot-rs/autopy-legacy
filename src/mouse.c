#include "mouse.h"
#include "screen.h"
#include "deadbeef_rand.h"
#include <math.h> /* For hypot() */

#if defined(IS_MACOSX)
	#include <ApplicationServices/ApplicationServices.h>
#elif defined(USE_X11)
	#include <X11/Xlib.h>
	#include <X11/extensions/XTest.h>
	#include "xdisplay.h"
#endif

#if !defined(IS_WINDOWS)
	/* Make sure nanosleep gets defined even when using C89. */
	#if !defined(__USE_POSIX199309) || !__USE_POSIX199309
		#define __USE_POSIX199309 1
	#endif

	#include <time.h> /* For nanosleep() */
#endif

#if defined(_MSC_VER)
	#define ssize_t SSIZE_T /* sigh */
#endif

void moveMouse(MMPoint point)
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
	point.x *= 0xFFFF / GetSystemMetrics(SM_CXSCREEN);
	point.y *= 0xFFFF / GetSystemMetrics(SM_CYSCREEN);
	mouse_event(MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE,
	            point.x, point.y, 0, 0);
#endif
}

MMPoint getMousePos()
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

void toggleMouse(bool down, MMMouseButton button)
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

void clickMouse(MMMouseButton button)
{
	toggleMouse(true, button);
	toggleMouse(false, button);
}

static void msleep(double milliseconds)
{
#if defined(WINDOWS)
	Sleep(milliseconds)
#else
	/* Technically, nanosleep() is not an ANSI function, but it is the most
	 * supported precise sleeping function I can find.
	 *
	 * If it is really necessary, it may be possible to emulate this with some
	 * hack using select() in the future if we really have to. */
	struct timespec time;
	time.tv_sec = milliseconds / 1000;
	time.tv_nsec = (milliseconds - (time.tv_sec * 1000)) * 1000000;
	nanosleep(&time, NULL);
#endif
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

		pos.x += (size_t)floor(velo_x + 0.5);
		pos.y += (size_t)floor(velo_y + 0.5);

		/* Make sure we are in the screen boundaries!
		 * (Strange things will happen if we are not.) */
		if (pos.x >= screenSize.width || pos.y >= screenSize.height) {
			return false;
		}

		moveMouse(pos);

		/* Wait 1 - 3 milliseconds. */
		msleep(DEADBEEF_UNIFORM(1.0, 3.0));
	}

	return true;
}
