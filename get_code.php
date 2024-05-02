<?php
    class CodeGenerator {
        function __construct() {
            $this->chars = 'CM7WD6N4RHF9ZL3XKQGVPBTJY';
            $this->base = strlen($this->chars);
            $this->epoch = DateTime::createFromFormat('Y-m-d H:i', '2016-02-01 00:00');
        }
        
        function encode($num) {
            if ($num < $this->base) {
                return $this->chars[$num];
            } else {
                return self::encode((int) (floor($num / $this->base))) . $this->chars[$num % $this->base];
            }
        }

        function decode($code, $multiplier=1) {
            $decoded = strpos($this->chars, substr($code, -1)) * $multiplier;

            if (strlen($code) > 1) {
                return self::decode(substr($code, 0, -1), $multiplier * $this->base) + $decoded;
            } else {
                return $decoded;
            }
        }

        function getOrderFlags($orderId, $visitType) {
            $flags = 0;

            $unknownFlag1 = $this->decode('MC');
            $unknownFlag2 = $this->decode('DC');

            if ($visitType === 3 || $visitType === 5) {
                $flags += $unknownFlag1;
            }

            $flags += $unknownFlag2;

            return $flags;
        }

        function getMinutesSinceEpoch($purchased) {
            $purchased = DateTime::createFromFormat('Y-m-d H:i', $purchased);
            return ($purchased->getTimestamp() - $this->epoch->getTimestamp()) / 60;
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

        function generateCode($storeId, $orderId, $purchased, $visitType=3) {
            $zero = $this->encode(0);
            $encStoreId = str_pad($this->encode($storeId), 3, $zero, STR_PAD_LEFT);
            $encVisitType = $this->encode($visitType);
            $encOrderId = $this->encode(($orderId % 100) + $this->getOrderFlags($orderId, $visitType));
            $encMinutes = str_pad($this->encode($this->getMinutesSinceEpoch($purchased)), 5, $zero, STR_PAD_LEFT);

            $code = $encStoreId . $encVisitType . $encOrderId . $encMinutes;

            $code .= $this->encode($this->getCheckDigit($code));

            return implode('-', str_split($code, 4));
        }
    };
