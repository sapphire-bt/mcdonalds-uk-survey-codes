<?php
    class CodeGenerator {
        function __construct() {
            $this->chars = 'CM7WD6N4RHF9ZL3XKQGVPBTJY';
            $this->base = strlen($this->chars);
            $this->epoch = DateTime::createFromFormat('Y-m-d H:i', '2016-02-01 00:00');
            $this->reg_delivery = 61;
        }

        function encode($num) {
            if ($num < $this->base) {
                return $this->chars[$num];
            } else {
                return $this->encode((int) (floor($num / $this->base))) . $this->chars[$num % $this->base];
            }
        }

        function decode($code, $multiplier=1) {
            $decoded = strpos($this->chars, substr($code, -1)) * $multiplier;

            if (strlen($code) > 1) {
                return $this->decode(substr($code, 0, -1), $multiplier * $this->base) + $decoded;
            } else {
                return $decoded;
            }
        }

        function getMinutesSinceEpoch($purchased) {
            $purchased = DateTime::createFromFormat('Y-m-d H:i', $purchased, new DateTimeZone('Europe/London'));
            $isDST = (bool) $purchased->format('I');
            $minutes = ($purchased->getTimestamp() - $this->epoch->getTimestamp()) / 60;

            if (!$isDST) {
                $minutes -= 60;
            }

            return $minutes;
        }

        function getCheckDigit($code) {
            $checkDigit = 0;
            $reversed = str_split(strrev($code));

            foreach ($reversed as $x => $char) {
                $val = $this->decode($char);

                if (($x % 2) === 0) {
                    $val *= 2;
                    $encVal = $this->encode($val);

                    if (strlen($encVal) === 2) {
                        $val = $this->decode($encVal[0]) + $this->decode($encVal[1]);
                    }
                }

                $checkDigit += $val;
            }

            $checkDigit %= $this->base;

            if ($checkDigit > 0) {
                $checkDigit = $this->base - $checkDigit;
            }

            return $checkDigit;
        }

        function generateCode($storeId, $orderId, $purchased, $reg=20) {
            $zero = $this->encode(0);
            $encStoreId = $this->encode($storeId);
            $encOrderId = $this->encode(($orderId % 100) + ($reg === $this->reg_delivery ? 0 : $reg * 100));
            $encMinutes = $this->encode($this->getMinutesSinceEpoch($purchased));

            $encStoreId = str_pad($encStoreId, 3, $zero, STR_PAD_LEFT);
            $encOrderId = str_pad($encOrderId, 3, $zero, STR_PAD_LEFT);
            $encMinutes = str_pad($encMinutes, 5, $zero, STR_PAD_LEFT);

            $code = $encStoreId . $encOrderId . $encMinutes;

            $code .= $this->encode($this->getCheckDigit($code));

            return implode('-', str_split($code, 4));
        }
    };
