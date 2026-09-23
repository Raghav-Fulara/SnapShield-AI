# SnapShield AI - Native Engine Makefile
# Targets: Linux/macOS shared object and cross-compilation reference

CC ?= gcc
CFLAGS ?= -O3 -fPIC -Wall -Wextra -I./include
LDFLAGS ?= -shared

TARGET = libsnapshield_core.so
SRCS = src/snapshield_simd_scanner.c
OBJS = $(SRCS:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $^
	@echo "[SUCCESS] Built native Qualcomm acceleration binary: $(TARGET)"

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f src/*.o $(TARGET)

.PHONY: all clean
